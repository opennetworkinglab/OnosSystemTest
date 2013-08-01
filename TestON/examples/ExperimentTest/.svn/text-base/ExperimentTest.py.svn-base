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
            
