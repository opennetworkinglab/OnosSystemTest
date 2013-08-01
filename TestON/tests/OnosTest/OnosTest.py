
class OnosTest :

    def __init__(self) :
        self.default = ''

    def CASE1(self,main) :

        main.case("Testing the ONOS sanity")
        main.step("Testing the ONOS sanity")
    
        Zookeeper1_status = main.Zookeeper1.status()
        main.log.info(Zookeeper1_status)
    
        Cassandra1_status = main.Cassandra1.status()
        main.log.info(Cassandra1_status)
    
        ONOS1_status = main.ONOS1.status()
        if ONOS1_status:
            main.log.info("ONOS is up") 
        else:
            main.log.info("ONOS is down") 
    
        ONOS1_rest_status = main.ONOS1.rest_status()
        main.log.info(ONOS1_rest_status)
    
        Response = main.ONOSRESTAPI1.execute()
        main.log.info(Response)
    
        main.ONOS1.stop()
        main.ONOS1.rest_stop()
        main.Cassandra1.stop()
        main.Zookeeper1.stop()
