class DpctlTest:
    '''
    Testing of the some basic Dpctl functions included here
    '''
    
    def __init__(self):
        self.default = ""
                
    def CASE1(self,main):
        '''
        Test to add the flow configuration by using dpctl and ping the host 
        '''
        main.case("DPCTL ping host ")
        main.step("adding flow for host2 ")
        main.DPCTL1.addFlow(tcpip=main.params['CASE1']['STEP1']['tcpip'],
                            tcpport=main.params['CASE1']['STEP1']['tcpport'],
                            inport=main.params['CASE1']['STEP1']['inport'],
                            timeout=main.params['CASE1']['STEP1']['timeout'],
                            action=main.params['CASE1']['STEP1']['action'])
        main.step("adding another flow for host3")
        main.DPCTL1.addFlow(tcpip=main.params['CASE1']['STEP2']['tcpip'],
                            tcpport=main.params['CASE1']['STEP2']['tcpport'],
                            inport=main.params['CASE1']['STEP2']['inport'],
                            timeout=main.params['CASE1']['STEP2']['timeout'],
                            action=main.params['CASE1']['STEP2']['action'])
        main.step("Ping from h2 to h3")
        result = main.Mininet1.pingHost(src=main.componentDictionary['DPCTL1']['src'],
                                        target=main.componentDictionary['DPCTL1']['target'],
                                        controller=main.componentDictionary['DPCTL1']['controller'])
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Show flow executed",onfail="Show flow execution Failed")


    def CASE2(self,main):
        '''
        Test to add the flow configuration by using dpctl and show the flow using dpctl  
        '''
        main.case("DPCTL show flow ")
        main.step("adding flow for host2")

        main.DPCTL1.addFlow(tcpip=main.params['CASE2']['STEP1']['tcpip'],
                            tcpport=main.params['CASE2']['STEP1']['tcpport'],
                            inport=main.params['CASE2']['STEP1']['inport'],
                            timeout=main.params['CASE2']['STEP1']['timeout'],
                            action=main.params['CASE2']['STEP1']['action'])
        main.step("adding flow for host3")
        main.DPCTL1.addFlow(tcpip=main.params['CASE2']['STEP2']['tcpip'],
                            tcpport=main.params['CASE2']['STEP2']['tcpport'],
                            inport=main.params['CASE2']['STEP2']['inport'],
                            timeout=main.params['CASE2']['STEP2']['timeout'],
                            action=main.params['CASE2']['STEP2']['action'])
        main.step("Execute Show flow ")
        result = main.DPCTL1.showFlow(tcpip=main.params['CASE2']['tcpip'],tcpport=main.params['CASE2']['tcpport'])
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Show flow executed",onfail="Show flow execution Failed")
            

