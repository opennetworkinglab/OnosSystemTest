
class MininetTest :

    def __init__(self) :
        self.default = ''

    def CASE1(self,main) :

        main.case("Testing the configuration of the host")
        main.step("Host IP Checking using checkIP")
        main.ONOS1.start()
        result = main.Mininet1.checkIP(main.params['CASE1']['destination'])
        main.step("Verifying the result")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Host h2 IP address configured",onfail="Host h2 IP address didn't configured")
    
    def CASE2(self,main) :

        main.case("Testing Reachabilty of all the hosts")
        main.step("Checking Hosts reachability by using pingall")
        result = main.Mininet1.pingall()
        main.step("Verifying the result")
        for source in  main.params['SET1']['begin']:
            main.log.info(str(main.params['SET1']['begin'][source]))
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="All hosts are reacchable",onfail="Hosts are not reachable")
