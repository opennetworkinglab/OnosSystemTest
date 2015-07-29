#!/usr/bin/env python
'''
Created on 26-Nov-2012

@author: Anil Kumar (anilkumar.s@paxterrasolutions.com)

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

'''
class CaseParams:
    '''
    This example shows the usage of the CASE level parameters, in params file the
    [[CASE]]
        'destination'  = 'h2'

    We can get this CASE level parameter like :
    main.params['CASE1']['destination']


    cd ~/bin/
    ofautomation>run CaseParams example 1
       will execute this example.
    '''

    def __init__(self):
        self.default = ""

    def CASE1(self,main):
        '''
        This test case will showcase usage of CASE level parameters to specify the host as h2
        '''
        main.case("Using CASE level parameters to specify the host as h2")
        main.step("Host IP Checking using checkIP")
        result = main.Mininet1.checkIP(main.params['CASE1']['destination'])
        main.step("Verifying the result")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Host h2 IP address configured",onfail="Host h2 IP address didn't configured")


    def CASE2(self,main):
        '''
        This test case will showcase usage of CASE level parameters to specify the host as h3
        '''
        main.case("Using CASE level parameters to specify the host as h3")
        main.step("Host IP Checking using checkIP")
        result = main.Mininet1.checkIP(main.params['CASE2']['destination'])
        main.step("Verifying the result")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Host h3 IP address configured",onfail="Host h3 IP address didn't configured")
