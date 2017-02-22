#!/usr/bin/python
'''
This script uses pexpect to talk to DELTA manager and triggers all CONTROL_PLANE_OF and
ADVANCED test cases. It also reads the DELTA log and prints the results for each case
'''

import sys
import pexpect
import time
import datetime

DELTA_DIR = '/home/sdn/DELTA'
DELTA_LOG = 'delta.log'
RESULT_FILE = 'summary.txt'
LOG_CHECK_INTERVAL = 10
# TODO: get attack codes from DELTA CLI
CODES = ['2.1.010','2.1.020','2.1.030','2.1.040','2.1.050','2.1.060','2.1.070','2.1.071','2.1.072','2.1.073','2.1.080','3.1.010','3.1.020','3.1.030','3.1.040','3.1.050','3.1.060','3.1.070','3.1.080','3.1.090','3.1.100','3.1.110','3.1.120','3.1.130','3.1.140','3.1.150','3.1.160','3.1.170','3.1.180','3.1.190','3.1.200']
CODE_TO_SKIP = ['3.1.090','3.1.160']
# Timeout for each test case
TIMEOUT = 1800

def triggerTest( handle, code ):
    testAvailable = True
    print datetime.datetime.now(), "Starting test", code
    # TODO: expect Exceptions thrown by DELTA
    i = handle.expect( ['Command>', pexpect.EOF, pexpect.TIMEOUT], 60 )
    if i != 0:
        print "pexpect EOF or TIMEOUT, exiting..."
        return -1
    time.sleep(0.5)

    handle.sendline( 'k' )
    i = handle.expect( ['Select the attack code>', pexpect.EOF, pexpect.TIMEOUT], 60 )
    if i != 0:
        print "pexpect EOF or TIMEOUT, exiting..."
        return -1
    time.sleep(0.5)

    handle.sendline( code )
    i = handle.expect( ['not available', 'Press ENTER key to continue..', pexpect.EOF, pexpect.TIMEOUT], 60 )
    if i == 0:
        testAvailable = False
    elif i == 1:
        testAvailable = True
    else:
        print "pexpect EOF or TIMEOUT, exiting..."
        return -1
    time.sleep(0.5)

    handle.sendline( '' )
    if not testAvailable:
        print "Test", code, "is not available"
        return 0

    return 1

def waitForTest( code ):
    startTime = time.time()
    while True:
        if time.time() - startTime > TIMEOUT:
            print "Test timeout, exiting..."
            return -1
        time.sleep( LOG_CHECK_INTERVAL )
        log = open( DELTA_LOG ).read()
        log = log.split( code )
        if len( log ) == 1:
            pass
        elif "done" in log[-1]:
            try:
                testName = log[1].split( ' - ' )[1]
            except IndexError:
                print "Error getting test name"
                testName = "Unknown Test Name"
            result = "UNKNOWN"
            if "FAIL" in log[-1]:
                result = "FAIL"
            elif "PASS" in log[-1]:
                result = "PASS"
            print datetime.datetime.now(), "Test result:", result, "Time taken:", time.time() - startTime, "seconds"
            resultFile = open( RESULT_FILE, 'a' )
            resultFile.write( code + " " + testName + ": " + result + "\n" )
            resultFile.close()
            return 1
        else:
            pass

def runTests():
    resultFile = open( RESULT_FILE, 'w' )
    resultFile.write( "Test started on " + str(datetime.datetime.now())+"\n" )
    resultFile.close()
    handle=pexpect.spawn( 'java -jar ' + DELTA_DIR + '/manager/target/delta-manager-1.0-SNAPSHOT-jar-with-dependencies.jar ' + DELTA_DIR + '/tools/config/manager.cfg' )
    for code in CODES:
        # Skip some broken cases
        if code in CODE_TO_SKIP:
            continue
        triggerResult = triggerTest( handle, code )
        # pexpect failures
        if triggerResult == -1:
            return
        # Test not available
        elif triggerResult == 0:
            continue
        testResult = waitForTest( code )
        # Test timed out
        if testResult == -1:
            break
    # Exit DELTA
    print "All tests done, exiting DELTA"
    i = handle.expect( ['Command>', pexpect.EOF, pexpect.TIMEOUT], 60 )
    handle.sendline( 'q' )

if __name__ == '__main__':
    if len( sys.argv ) >= 2:
        DELTA_DIR = sys.argv[1]
    print 'DELTA directory is', DELTA_DIR
    runTests()
