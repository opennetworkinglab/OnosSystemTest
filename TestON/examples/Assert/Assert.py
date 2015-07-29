'''

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
class Assert :

    def __init__(self) :
        self.default = ''

    def CASE1(self,main) :


        main.case("Using assert to verify the result")
        main.step("Using assert_equal to verify the result is equivalent or not")
        expect = main.TRUE
        actual = main.TRUE
        main.log.warn(main.response_parser('<real></real><imag>2</imag><__complex__>true</__complex__>', "json"))
        utilities.assert_equals(expect=expect,actual=actual,onpass="expect is equal to actual",onfail="expect is not equal to actual")

        main.step("Using assert_matches to verify the result matches or not")
        expect = "Res(.*)"
        actual = "Result"
        utilities.assert_matches(expect=expect,actual=actual,onpass="expect is macthes to actual",onfail="expect is not matches to actual")

        main.step("Using assert_greater to verify the result greater or not")
        expect = 10
        actual = 5
        utilities.assert_greater(expect=actual,actual=expect,onpass="expect is greater than the actual",onfail="expect is not greater than the actual")

        main.step("Using assert_lesser to verify the result lesser or not")
        expect = 5
        actual = 10
        utilities.assert_lesser(expect=actual,actual=expect,onpass="expect is lesser than the actual",onfail="expect is not lesser than the actual")
