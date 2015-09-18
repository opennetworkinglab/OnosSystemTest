'''
    Wrapper functions for maxIntent
'''

import json
import time
import pexpect

def __init__( self ):
    self.default = ""

def getIntents( main, state="INSTALLED", sleep=1, timeout=120 ):
    intents = 0
    try:
        cmd = "intents | grep " + state + " | wc -l"
        main.log.info("Sending: " + cmd)
        main.CLIs[0].handle.sendline(cmd)

        time.sleep(sleep)

        main.CLIs[0].handle.expect("onos>", timeout=timeout)
        raw = main.CLIs[0].handle.before
        intents = int(main.CLIs[0].handle.before.split()[7])
        main.log.info(state + " intents: " + str(intents))
    except pexpect.TIMEOUT:
        main.log.exception("Timeout exception caught in getIntent")
    return intents

def getFlows( main, state="ADDED", sleep=1, timeout=120 ):
    flows = 0
    try:
        cmd = "flows | grep " + state + " | wc -l"
        main.log.info("Sending: " + cmd)
        main.CLIs[0].handle.sendline(cmd)

        time.sleep(sleep)

        main.CLIs[0].handle.expect("onos>", timeout=timeout)
        raw = main.CLIs[0].handle.before
        flows = int(main.CLIs[0].handle.before.split()[7])
        main.log.info(state + " flows: " + str(flows))
    except pexpect.TIMEOUT:
        main.log.exception("Timeout exception caught in getFlows")
    return flows


def pushIntents( main,
                 switch,
                 ingress,
                 egress,
                 batch,
                 offset,
                 sleep=1,
                 options="",
                 timeout=120):
    '''
        Pushes intents using the push-test-intents cli command.
    '''
    try:
        cmd = "push-test-intents " + options + " " + switch + ingress + " " +\
                switch + egress + " " + str(batch) + " " + str(offset)
        main.log.info("Installing " + str(offset+batch) + " intents")
        main.log.debug("Sending: " + cmd)
        main.CLIs[0].handle.sendline(cmd)
        time.sleep(sleep)
        main.CLIs[0].handle.expect("onos>", timeout=timeout)

        raw = main.CLIs[0].handle.before
        if "Failure:" not in raw and "GC" not in raw:
            return main.TRUE
    except pexpect.TIMEOUT:
        main.log.exception("Timeout exception caught in pushIntents")
    return main.FALSE

def verifyFlows( main, expectedFlows, state="ADDED", sleep=1, numcheck=10, timeout=120):
    '''
        This function returns main.TRUE if the number of expected flows are in
        the specified state

        @params
            expectedFlows: the flows you expect to see in the specified state
            state: the state of the flow to check for
            sleep: how long it should sleep for each check
            numcheck: how many times it should check
            timeout: the timeout for pexpect
    '''
    cmd = "flows | grep " + state + " | wc -l"
    for i in range(numcheck):
        flows = getFlows( main, state, sleep, timeout )
        if expectedFlows == flows:
            return main.TRUE

    return main.FALSE

def verifyIntents( main, expectedIntents, state="INSTALLED", sleep=1, numcheck=10, timeout=120):
    '''
        This function returns main.TRUE if the number of expected intents are in
        the specified state

        @params
            expectedFlows: the intents you expect to see in the specified state
            state: the state of the intent to check for
            sleep: how long it should sleep for each check
            numcheck: how many times it should check
            timeout: the timeout for pexpect
    '''
    cmd = "intents | grep " + state + " | wc -l"
    for i in range(numcheck):
        intents = getIntents( main, state, sleep, timeout )
        if expectedIntents == intents:
            return main.TRUE
        time.sleep(sleep)

    return main.FALSE
