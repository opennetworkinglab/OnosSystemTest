"""
Copyright 2016 Open Networking Foundation (ONF)

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.
"""

'''
    Wrapper function for SCPFswitchLat test
    Assign switch and capture openflow package
    remove switch and caputer openflow package
    calculate latency
'''
import time
import json

def getTimestampFromLog( index, searchTerm ):
    '''
    Get timestamp value of the search term from log.
    Args:
        index: the index of cli
        searchTerm: the key term of timestamp

    '''
    lines = main.Cluster.active( index ).CLI.logSearch( mode='last', searchTerm=searchTerm )
    try:
        assert lines != None
        logString = lines[ len ( lines ) - 1 ]
        #get the target value
        line = logString.split( "time = " )
        key = line[ 1 ].split( " " )
        return int( key[ 0 ] )
    except IndexError:
        main.log.warn( "Index Error!" )
        return 0
    except AssertionError:
        main.log.warn( "Search Term Not Found" )
        return 0

def processPackage( package ):
    '''
    split package information to dictionary
    Args:
        package: Package String

    '''
    pacakge = package.split( " " )
    dic = {}
    for s in pacakge:
        try:
            [ key, value ] = s.split( "=" )
            dic[ key ] = value
        except:
            continue
    return dic

def findSeqBySeqAck( seq, packageList ):
    '''
    Find specific Seq of package in packageList
    Args:
        seq: seq from last TCP package
        packageList: find package in packageList

    '''
    for l in packageList:
        temp = processPackage( l )
        tA = temp[ 'Ack' ]
        if int( seq ) + 1 == int( tA ):
            return temp[ 'Seq' ]

def arrangeTsharkFile( switchStatus, keyTerm ):
    '''
    Arrange different tshark messeage from overall file to different specific files
    Args:
        switchStatus: switch up or down
        keyTerm: A dictionary that store the path name as value and the searchTerm as key

    '''
    with open( main.tsharkResultPath[ switchStatus ][ 'ALL' ], 'r' ) as resultFile:
        resultText = resultFile.readlines()
        resultFile.close()

    for line in resultText:
        for term in keyTerm:
            if term in line:
                path = '/tmp/Tshark_' + str( keyTerm[ term ] )
                with open( path, 'a' ) as outputfile:
                    outputfile.write( line )
                    outputfile.close()

def checkResult( result1, result2, result3 ):
    '''
    Check if the inputs meet the requirement
    Returns:
            1 means the results are right, 0 means the results are wrong

    '''
    result = check( result1 ) + check( result2 ) + check( result3 )
    if result < 3:
        # if any result is wrong, increase the main wrong number
        main.wrong[ 'checkResultIncorrect' ] += 1
        main.wrong[ 'totalWrong' ] += 1
        checkTotalWrongNum()
        return 0
    return 1

def check( result ):
    '''
    Check the single input.
    Returns:
            1 means the input is good, 0 means the input is wrong

    '''
    if result < int( main.resultRange[ 'Min' ] ) or result > int( main.resultRange[ 'Max' ] ):
        main.log.debug( str( result ) + " is not meet the requirement" )
        return 0
    return 1

def checkTotalWrongNum():
    '''
    Check if the total wrong number is bigger than the max wrong number. If it is, then exit the
    test.

    '''
    # if there are too many wrongs in this test, then exit
    if main.wrong['totalWrong'] > main.maxWrong:
        main.log.error( "The total wrong number exceeds %d, test terminated" % main.maxWrong )
        main.cleanup()
        main.exit()

def captureOfPack( main, deviceName, ofPack, switchStatus, resultDict, warmup ):
    '''

    Args:
        main: TestON class
        deviceName: device name
        ofPack: openflow package key word
        switchStatus: Up -- assign, down -- remove
        resultDict: dictionary to contain result
        warmup: warm up boolean

    '''
    main.log.debug( "TOTAL WRONG: " + str( main.wrong ) )
    for d in ofPack[ switchStatus ]:
        main.log.info( "Clean up Tshark" )
        with open( main.tsharkResultPath[ switchStatus ][ d ], "w" ) as tshark:
            tshark.write( "" )
    # use one tshark to grep everything
    # Get the grep string
    grepString = ''
    keyTerm = {}
    for d in ofPack[ switchStatus ]:
        grepString = grepString + ofPack[ switchStatus ][ d ] + '|'
        # get rid of regular experssion format
        cleanTerm = ofPack[ switchStatus ][ d ].replace( '\\', '' )
        keyTerm[ cleanTerm ] = d
    # Delete the last '|'
    grepString = grepString[:-1]
    # open tshark
    main.log.info( "starting tshark capture" )
    main.ONOSbench.tsharkGrep( grepString, main.tsharkResultPath[ switchStatus ][ 'ALL' ], grepOptions='-E' )
    if switchStatus == 'up':
        # if up, assign switch to controller
        time.sleep( main.measurementSleep )
        main.log.info( 'Assigning {} to controller'.format( deviceName ))
        main.Mininet1.assignSwController( sw=deviceName, ip=main.Cluster.active( 0 ).ipAddress )
        time.sleep( main.measurementSleep )
    if switchStatus == 'down':
        # if down, remove switch from topology
        time.sleep( main.measurementSleep )
        main.step( 'Remove switch from controler' )
        main.Mininet1.deleteSwController( deviceName )
        time.sleep( main.deleteSwSleep )
    main.log.info( "Stopping all Tshark processes" )
    main.ONOSbench.tsharkStop()
    tempResultDict = {}
    arrangeTsharkFile( switchStatus, keyTerm )

    if switchStatus == 'up':
        for d in main.tsharkResultPath[ 'up' ]:
            with open( main.tsharkResultPath[ switchStatus ][ d ], "r" ) as resultFile:
                # grep tshark result timestamp
                resultText = resultFile.readlines()
                if d == "TCP":
                    # if TCP package, we should use the latest one package
                    resultText = resultText[ len( resultText ) - 1 ]
                else:
                    resultText = resultText[ 0 ]
                main.log.info( "Capture result:" + resultText )
                resultText = resultText.strip()
                resultText = resultText.split( " " )
                if len(resultText) > 1:
                    tempResultDict[d]= int( ( float( resultText[ 1 ] ) * 1000 ) )
                resultFile.close()
    elif switchStatus == 'down':
        # if state is down, we should capture Fin/Ack and ACK package
        # Use seq number in FIN/ACK package to located ACK package
        with open( main.tsharkResultPath[ 'down' ][ 'FA' ], 'r' ) as resultFile:
            resultText = resultFile.readlines()
            FinAckText = resultText.pop( 0 )
            resultFile.close()
        FinAckSeq = processPackage( FinAckText )[ 'Seq' ]
        FinAckOFseq = findSeqBySeqAck( FinAckSeq, resultText )
        if FinAckOFseq == None:
            main.log.warn( "Tshark Result was incorrect!" )
            main.log.warn( resultText )
            main.wrong[ 'TsharkValueIncorrect' ] += 1
            main.wrong[ 'totalWrong' ] += 1
            checkTotalWrongNum()
            return
        with open( main.tsharkResultPath[ 'down' ][ 'ACK' ], "r" ) as resultFile:
            ACKlines = resultFile.readlines()
            resultFile.close()
        AckPackage = ""
        for l in ACKlines:
            temp = processPackage( l )
            finSeq = findSeqBySeqAck( FinAckOFseq, ACKlines )
            if temp[ 'Seq' ] == finSeq:
                AckPackage = l
        if len( AckPackage ) > 0:
            FinAckText = FinAckText.strip()
            FinAckText = FinAckText.split( " " )
            AckPackage = AckPackage.strip()
            AckPackage = AckPackage.split( " " )
            tempResultDict[ 'ACK' ] = int( float( AckPackage[ 1 ] ) * 1000 )
            tempResultDict[ 'FA' ] = int( float( FinAckText[ 1 ] ) * 1000 )
        else:
            main.wrong[ 'skipDown' ] += 1
            main.wrong[ 'totalWrong' ] += 1
            checkTotalWrongNum()
            return

    # calculate latency
    if switchStatus == "up":
        # up Latency
        for d in resultDict[ switchStatus ]:
            T_Ftemp = 0
            F_Rtemp = 0
            RQ_RRtemp = 0
            try:
                T_Ftemp = tempResultDict[ 'Feature' ] - tempResultDict[ 'TCP' ]
                F_Rtemp = tempResultDict[ 'RQ' ] - tempResultDict[ 'Feature' ]
                RQ_RRtemp = tempResultDict[ 'RR' ] - tempResultDict[ 'RQ' ]
            except KeyError:
                main.log.warn( "Tshark Result was incorrect!" )
                main.log.warn( tempResultDict )
                main.wrong[ 'TsharkValueIncorrect' ] += 1
                main.wrong[ 'totalWrong' ] += 1
                checkTotalWrongNum()
                return
            if not warmup:
                resultDict[ switchStatus ][ d ][ 'T_F' ].append( T_Ftemp )
                resultDict[ switchStatus ][ d ][ 'F_R' ].append( F_Rtemp  )
                resultDict[ switchStatus ][ d ][ 'RQ_RR' ].append( RQ_RRtemp )

            main.log.info( "{} TCP to Feature: {}".format( d, str( T_Ftemp ) ) )
            main.log.info( "{} Feature to Role Request: {}".format( d, str( F_Rtemp ) ) )
            main.log.info( "{} Role Request to Role Reply: {}".format( d, str( RQ_RRtemp ) ) )

        for i in range( 1, main.Cluster.numCtrls + 1 ):
            RR_Dtemp = 0
            D_Gtemp = 0
            E_Etemp = 0
            main.log.info( "================================================" )
            # get onos metrics timestamps
            try:
                response = json.loads( main.Cluster.active( i - 1 ).CLI.topologyEventsMetrics() )
                DeviceTime = getTimestampFromLog( i - 1, searchTerm=main.searchTerm[switchStatus] )
                main.log.info( "ONOS{} device Event timestamp: {}".format( i, "%.2f" % DeviceTime ) )
                GraphTime = int( response.get( "topologyGraphEventTimestamp" ).get( "value" ) )
                main.log.info( "ONOS{} Graph Event timestamp: {}".format( i, GraphTime ) )
            except TypeError:
                main.log.warn( "TypeError" )
                main.wrong[ 'TypeError' ] += 1
                main.wrong[ 'totalWrong' ] += 1
                checkTotalWrongNum()
                break
            except ValueError:
                main.log.warn( "Error to decode Json object!" )
                main.wrong[ 'decodeJasonError' ] += 1
                main.wrong[ 'totalWrong' ] += 1
                checkTotalWrongNum()
                break
            if DeviceTime != 0:
                try:
                    RR_Dtemp = DeviceTime - tempResultDict[ 'RR' ]
                    D_Gtemp = GraphTime - DeviceTime
                    E_Etemp = GraphTime - tempResultDict[ 'TCP' ]
                    check = checkResult( RR_Dtemp, D_Gtemp, E_Etemp )
                    if check == 1:
                        main.log.info( "Role reply to Device:{}".format( RR_Dtemp ) )
                        main.log.info( "Device to Graph:{}".format( D_Gtemp ) )
                        main.log.info( "End to End:{}".format( E_Etemp ) )
                        main.log.info( "================================================" )
                except KeyError:
                    main.log.warn( "Tshark Result was incorrect!" )
                    main.log.warn( tempResultDict )
                    main.wrong[ 'TsharkValueIncorrect' ] += 1
                    main.wrong[ 'totalWrong' ] += 1
                    checkTotalWrongNum()
                    return
                except TypeError:
                    main.log.warn( "TypeError" )
                    main.wrong[ 'TypeError' ] += 1
                    main.wrong[ 'totalWrong' ] += 1
                    checkTotalWrongNum()
                    break
                except ValueError:
                    main.log.warn( "Error to decode Json object!" )
                    main.wrong[ 'decodeJasonError' ] += 1
                    main.wrong[ 'totalWrong' ] += 1
                    checkTotalWrongNum()
                    break
                if not warmup and check == 1:
                    resultDict[ switchStatus ][ 'node' + str( i )][ 'RR_D' ].append( RR_Dtemp )
                    resultDict[ switchStatus ][ 'node' + str( i )][ 'D_G' ].append( D_Gtemp )
                    resultDict[ switchStatus ][ 'node' + str( i )][ 'E_E' ].append( E_Etemp )
            else:
                main.wrong['checkResultIncorrect'] += 1
                main.wrong[ 'totalWrong' ] += 1
                checkTotalWrongNum()
                main.log.debug("Skip this iteration due to the None Devicetime")

    if switchStatus == "down":
        # down Latency
        for d in resultDict[ switchStatus ]:
            FA_Atemp = 0
            try:
                FA_Atemp = tempResultDict[ 'ACK' ] - tempResultDict[ 'FA' ]
            except KeyError:
                main.log.warn( "Tshark Result was incorrect!" )
                main.log.warn( tempResultDict )
                main.wrong[ 'TsharkValueIncorrect' ] += 1
                main.wrong[ 'totalWrong' ] += 1
                checkTotalWrongNum()
                return
            if not warmup:
                resultDict[ switchStatus ][ d ][ 'FA_A' ].append( FA_Atemp )
            main.log.info( "{} FIN/ACK TO ACK {}:".format( d, FA_Atemp ) )
        for i in range( 1, main.Cluster.numCtrls + 1 ):
            A_Dtemp = 0
            D_Gtemp = 0
            E_Etemp = 0
            main.log.info( "================================================" )
            # get onos metrics timestamps
            try:
                response = json.loads( main.Cluster.active( i - 1 ).CLI.topologyEventsMetrics() )
                DeviceTime = getTimestampFromLog( i - 1, searchTerm=main.searchTerm[ switchStatus ] )
                main.log.info( "ONOS{} device Event timestamp: {}".format( i, DeviceTime ) )
                GraphTime = int( response.get( "topologyGraphEventTimestamp" ).get( "value" ) )
                main.log.info( "ONOS{} Graph Event timestamp: {}".format( i, GraphTime ) )
            except TypeError:
                main.log.warn( "TypeError" )
                main.wrong[ 'TypeError' ] += 1
                main.wrong[ 'totalWrong' ] += 1
                checkTotalWrongNum()
                break
            except ValueError:
                main.log.warn( "Error to decode Json object!" )
                main.wrong[ 'decodeJasonError' ] += 1
                main.wrong[ 'totalWrong' ] += 1
                checkTotalWrongNum()
                break
            if DeviceTime != 0:
                main.log.info( "================================================" )
                try:
                    A_Dtemp = DeviceTime - tempResultDict[ 'ACK' ]
                    D_Gtemp = GraphTime - DeviceTime
                    E_Etemp = GraphTime - tempResultDict[ 'FA' ]
                    check = checkResult( A_Dtemp, D_Gtemp, E_Etemp )
                    if check == 1:
                        main.log.info( "ACK to device: {}".format( A_Dtemp ) )
                        main.log.info( "Device to Graph: {}".format( D_Gtemp )  )
                        main.log.info( "End to End: {}".format( E_Etemp ) )
                        main.log.info( "================================================" )
                except KeyError:
                    main.log.warn( "Tshark Result was incorrect!" )
                    main.log.warn( tempResultDict )
                    main.wrong[ 'TsharkValueIncorrect' ] += 1
                    main.wrong[ 'totalWrong' ] += 1
                    checkTotalWrongNum()
                    return
                except TypeError:
                    main.log.warn( "TypeError" )
                    main.wrong[ 'TypeError' ] += 1
                    main.wrong[ 'totalWrong' ] += 1
                    checkTotalWrongNum()
                    break
                except ValueError:
                    main.log.warn( "Error to decode Json object!" )
                    main.wrong[ 'decodeJasonError' ] += 1
                    main.wrong[ 'totalWrong' ] += 1
                    checkTotalWrongNum()
                    break
                if not warmup and check == 1:
                    resultDict[ switchStatus ][ 'node' + str( i ) ][ 'A_D' ].append( A_Dtemp )
                    resultDict[ switchStatus ][ 'node' + str( i ) ][ 'D_G' ].append( D_Gtemp )
                    resultDict[ switchStatus ][ 'node' + str( i ) ][ 'E_E' ].append( E_Etemp )

            else:
                main.wrong['checkResultIncorrect'] += 1
                main.wrong['totalWrong'] += 1
                checkTotalWrongNum()
                main.log.debug("Skip this iteration due to the None Devicetime")

