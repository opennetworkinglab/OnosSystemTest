class PoxTest:
    '''
    Testing Basic Pox Functionalities
    '''
    def __init__(self):
        self.default = ""

    def CASE1(self,main):
        main.case("Checking the control flow of POX")
        main.step("Checking the host reachability using pingHost ")
        
        result = main.Mininet1.pingHost(src=main.params['CASE1']['src'],
                                        target=main.params['CASE1']['target'],
                                        controller=main.params['CASE1']['controller'])
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Ping executed successfully",onfail="Ping Failed")
