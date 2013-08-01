'''
	
 *   TestON is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation, either version 2 of the License, or
 *   (at your option) any later version.

 *   TestON is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.


'''

class PoxTest :

    def __init__(self) :
        self.default = ''

    def CASE1(self,main) :

        main.case("Checking the control flow of POX")
        main.step("Checking the host reachability using pingHost")
        main.Mininet1.pingHost(src=main.params['CASE1']['src'], target=main.params['CASE1']['target'], controller=main.params['CASE1']['controller'])
        result = main.last_result
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Ping executed successfully",onfail="Ping failed")
    
    
