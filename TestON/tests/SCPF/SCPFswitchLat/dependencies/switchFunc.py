'''
    Wrapper function for SCPFswitchLat test
    Assign switch and capture openflow package
    remove switch and caputer openflow package
    calculate latency
'''


import time
import json
def processPackage( package ):
    '''
    split package information to dictionary
    Args:
        package: Package String

    Returns:

    '''
    pacakge = package.split(" ")
    dic = {}
    for s in pacakge:
        try:
            [key, value] = s.split("=")
            dic[key] = value
        except:
            continue
    return dic

def findSeqBySeqAck( seq, packageList):
    '''
    Find specific Seq of package in packageList
    Args:
        seq: seq from last TCP package
        packageList: find package in packageList

    Returns:

    '''
    for l in packageList:
        temp = processPackage(l)
        tA = temp['Ack']
        if int(seq) + 1 == int(tA):
            return temp['Seq']

def captureOfPack( main, deviceName, ofPack, switchStatus, resultDict, warmup ):
    '''

    Args:
        main: TestON class
        deviceName: device name
        ofPack: openflow package key word
        switchStatus: Up -- assign, down -- remove
        resultDict: dictionary to contain result
        warmup: warm up boolean

    Returns:

    '''
    for d in ofPack[switchStatus]:
        main.log.info("Clean up Tshark")
        with open(main.tsharkResultPath[switchStatus][d], "w") as tshark:
            tshark.write("")
        main.log.info( "Starting tshark capture" )
        main.ONOSbench.tsharkGrep(ofPack[switchStatus][d], main.tsharkResultPath[switchStatus][d])
    if switchStatus == 'up':
        # if up, assign switch to controller
        time.sleep(main.measurementSleep)
        main.log.info('Assigning {} to controller'.format(deviceName))
        main.Mininet1.assignSwController(sw=deviceName, ip=main.ONOSip[0])
        time.sleep(main.measurementSleep)
    if switchStatus == 'down':
        # if down, remove switch from topology
        time.sleep(main.measurementSleep)
        main.step('Remove switch from controller')
        main.Mininet1.deleteSwController(deviceName)
        time.sleep(10)
    main.log.info( "Stopping all Tshark processes" )
    main.ONOSbench.tsharkStop()
    tempResultDict = {}
    if switchStatus == 'up':
        for d in main.tsharkResultPath['up']:
            with open(main.tsharkResultPath[switchStatus][d], "r") as resultFile:
                # grep tshark result timestamp
                resultText = resultFile.readlines()
                if d == "TCP":
                    # if TCP package, we should use the latest one package
                    resultText = resultText[len(resultText) - 1]
                else:
                    resultText = resultText[0]
                main.log.info("Capture result:" + resultText)
                resultText = resultText.strip()
                resultText = resultText.split( " " )
                if len(resultText) > 1:
                    tempResultDict[d]= int( ( float(resultText[1]) * 1000 ) )
                resultFile.close()
    elif switchStatus == 'down':
        # if state is down, we should capture Fin/Ack and ACK package
        # Use seq number in FIN/ACK package to located ACK package
        with open(main.tsharkResultPath['down']['FA']) as resultFile:
            resultText = resultFile.readlines()
            FinAckText = resultText.pop(0)
            resultFile.close()
        FinAckSeq = processPackage(FinAckText)['Seq']
        FinAckOFseq = findSeqBySeqAck(FinAckSeq, resultText)

        with open(main.tsharkResultPath['down']['ACK']) as resultFile:
            ACKlines = resultFile.readlines()
            resultFile.close()

        AckPackage = ""
        for l in ACKlines:
            temp = processPackage(l)
            if temp['Seq'] == findSeqBySeqAck(FinAckOFseq, ACKlines):
                AckPackage = l
        if len(AckPackage) > 0:
            FinAckText = FinAckText.strip()
            FinAckText = FinAckText.split(" ")
            AckPackage = AckPackage.strip()
            AckPackage = AckPackage.split(" ")
            tempResultDict['ACK'] = float("%.2f" % (float(AckPackage[1]) * 1000) )
            tempResultDict['FA'] = float("%.2f" % (float(FinAckText[1]) * 1000) )
        else:
            return
    # calculate latency
    if switchStatus == "up":
        # up Latency
        for d in resultDict[switchStatus]:
            T_Ftemp = 0
            F_Rtemp = 0
            RQ_RRtemp = 0
            try:
                T_Ftemp = tempResultDict['Feature'] - tempResultDict['TCP']
                F_Rtemp = tempResultDict['RQ'] - tempResultDict['Feature']
                RQ_RRtemp = tempResultDict['RR'] - tempResultDict['RQ']
            except KeyError:
                main.log.warn("Tshark Result was incorrect!")
                main.log.warn(tempResultDict)
                return
            if not warmup:
                resultDict[switchStatus][d][ 'T_F' ].append( T_Ftemp )
                resultDict[switchStatus][d][ 'F_R' ].append( F_Rtemp  )
                resultDict[switchStatus][d][ 'RQ_RR' ].append( RQ_RRtemp )

            main.log.info("{} TCP to Feature: {}".format(d, str( T_Ftemp ) ) )
            main.log.info("{} Feature to Role Request: {}".format(d, str(F_Rtemp)))
            main.log.info("{} Role Request to Role Reply: {}".format(d, str(RQ_RRtemp)))

        for i in range(1, main.numCtrls + 1):
            RR_Dtemp = 0
            D_Gtemp = 0
            E_Etemp = 0
            main.log.info("================================================")
            # get onos metrics timestamps
            try:
                response = json.loads(main.CLIs[i - 1].topologyEventsMetrics())
                DeviceTime = int( response.get("topologyDeviceEventTimestamp").get("value") )
                main.log.info("ONOS{} device Event timestamp: {}".format(i, "%.2f" % DeviceTime))
                GraphTime = int( response.get("topologyGraphEventTimestamp").get("value") )
                main.log.info("ONOS{} Graph Event timestamp: {}".format(i, GraphTime))
            except TypeError:
                main.log.warn("TypeError")
                break
            except ValueError:
                main.log.warn("Error to decode Json object!")
                break
            try:
                RR_Dtemp = DeviceTime - tempResultDict['RR']
                D_Gtemp = GraphTime - DeviceTime
                E_Etemp = GraphTime - tempResultDict['TCP']
                main.log.info("Role reply to Device:{}".format(RR_Dtemp))
                main.log.info("Device to Graph:{}".format(D_Gtemp))
                main.log.info("End to End:{}".format(E_Etemp))
                main.log.info("================================================")
            except KeyError:
                main.log.warn("Tshark Result was incorrect!")
                main.log.warn(tempResultDict)
                return
            except TypeError:
                main.log.warn("TypeError")
                break
            except ValueError:
                main.log.warn("Error to decode Json object!")
                break
            if not warmup:
                resultDict[switchStatus]['node' + str(i)][ 'RR_D' ].append( RR_Dtemp )
                resultDict[switchStatus]['node' + str(i)][ 'D_G' ].append( D_Gtemp )
                resultDict[switchStatus]['node' + str(i)][ 'E_E' ].append( E_Etemp )

            main.log.info( "{} Role Reply to Device: {}".format( d, str(RR_Dtemp) ) )
            main.log.info( "{} Device to Graph: {}".format( d, str(D_Gtemp) ) )
            main.log.info( "{} End to End: {}".format( d, str(E_Etemp) ) )

    if switchStatus == "down":
        # down Latency
        for d in resultDict[switchStatus]:
            FA_Atemp = 0
            try:
                FA_Atemp = float("%.2f" % (tempResultDict['ACK'] - tempResultDict['FA']) )
            except KeyError:
                main.log.warn("Tshark Result was incorrect!")
                main.log.warn(tempResultDict)
                return
            if not warmup:
                resultDict[switchStatus][d][ 'FA_A' ].append( FA_Atemp )
            main.log.info( "{} FIN/ACK TO ACK {}:".format(d , FA_Atemp) )
        for i in range(1, main.numCtrls + 1):
            A_Dtemp = 0
            D_Gtemp = 0
            E_Etemp = 0

            main.log.info("================================================")
            # get onos metrics timestamps
            try:
                response = json.loads(main.CLIs[i - 1].topologyEventsMetrics())
                DeviceTime = int( response.get("topologyDeviceEventTimestamp").get("value") )
                main.log.info("ONOS{} device Event timestamp: {}".format(i, DeviceTime))
                GraphTime = int( response.get("topologyGraphEventTimestamp").get("value") )
                main.log.info("ONOS{} Graph Event timestamp: {}".format(i, GraphTime))
            except TypeError:
                main.log.warn("TypeError")
                break
            except ValueError:
                main.log.warn("Error to decode Json object!")
                break
            main.log.info("================================================")
            try:
                A_Dtemp = float("%.2f" % (DeviceTime - tempResultDict['ACK']) )
                D_Gtemp = GraphTime - DeviceTime
                E_Etemp = float("%.2f" % (GraphTime - tempResultDict['FA']) )
                main.log.info("ACK to device: {}".format(A_Dtemp))
                main.log.info("Device ot Graph: {}".format(D_Gtemp))
                main.log.info("End to End: {}".format(E_Etemp))
                main.log.info("================================================")
            except KeyError:
                main.log.warn("Tshark Result was incorrect!")
                main.log.warn(tempResultDict)
                return
            except TypeError:
                main.log.warn("TypeError")
                break
            except ValueError:
                main.log.warn("Error to decode Json object!")
                break
            if not warmup:
                resultDict[switchStatus]['node' + str(i)][ 'A_D' ].append( A_Dtemp )
                resultDict[switchStatus]['node' + str(i)][ 'D_G' ].append( D_Gtemp )
                resultDict[switchStatus]['node' + str(i)][ 'E_E' ].append( E_Etemp )
        main.CLIs[0].removeDevice( "of:0000000000000001" )

