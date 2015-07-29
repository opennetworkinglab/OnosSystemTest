#!/usr/bin/env python
'''
Created on 26-Nov-2012

@author: Raghav Kashyap(raghavkashyap@paxterrasolutions.com)


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

Testing of the Experimental Mode

ofautomation>run ExperimentTest example 1
    will execute this example.
'''
class ExperimentTest:
    '''
    Testing of the Experimental Mode

    '''

    def __init__(self):
        self.default = ""

    def CASE1(self,main):
        '''
        Testing the configuration of the host by using checkIP functionof Mininet driver
        '''
        main.EXPERIMENTAL_MODE = main.TRUE
        main.case("Testing the configuration of the host")
        main.step("Host IP Checking using checkIP")
        result = main.Mininet1.checkIP(main.params['CASE1']['destination'])
        main.step("Verifying the result")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Host h2 IP address configured",onfail="Host h2 IP address didn't configured")
        main.step("Calling Non Existing API for Experimental Mode")
        testReturn = main.POX2.verify_flow(returns=main.TRUE)
        utilities.assert_equals(expect=main.TRUE,actual=testReturn,onpass="Host h2 IP address configured",onfail="Host h2 IP address didn't configured")

    def CASE2(self,main):
        '''
        Testing of the reachability of the hosts by using pingall of Mininet driver
        '''
        main.EXPERIMENTAL_MODE = main.TRUE
        main.case("Testing Reachabilty of all the hosts")
        main.step("Checking Hosts reachability by using pingall")
        result = main.Mininet1.pingall()
        main.step("Verifying the result")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="All hosts are reacchable",onfail="Hosts are not reachable")
        main.step("Calling Non Existing API for Experimental Mode")
        testReturn = main.Mininet1.verify_flow(returns=main.TRUE)
        utilities.assert_equals(expect=main.TRUE,actual=testReturn,onpass="Host h2 IP address configured",onfail="Host h2 IP address didn't configured")

