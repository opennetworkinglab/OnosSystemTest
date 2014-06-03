class ONOSSanity4 :
    def __init__(self) :
        self.default = ''

#************************************************************************************************************************************
    '''
    CASE1: Initial Startup
    This case will follow the following steps
    1. Stop all instances of Zookeeper, RAMCloud, and ONOS
    2. Pull and build (if necessary) the latest ONOS code from Gerrit
    3. Start Up Zookeeper, RAMCloud, and ONOS. (We will be using the start_all function aka ./onos.sh start)
    4. Start up Mininet (Omitted for now as the Mininet is started up when the handle is connected)
    5. Start up Rest Server
    6. Test startup of Zookeeper
    7. Test startup of RAMCloud
    8. Test startup of ONOS
    9. Test startup of Rest Server
    10. Test startup of Mininet
    '''
    def CASE1(self,main) :
        main.case("Initial Startup")
        main.step("\n*************************\nStop all instances of ZK, RC, and ONOS\n*******************\n")
        main.ONOS1.stop()
        main.ONOS2.stop()
        main.ONOS3.stop()
        main.ONOS4.stop()
        main.RC1.stop_serv()
        main.RC2.stop_serv()
        main.RC3.stop_serv()
        main.RC4.stop_serv()
        main.RC1.stop_coor()
        main.Zookeeper1.stop()
        main.Zookeeper2.stop()
        main.Zookeeper3.stop()
        main.Zookeeper4.stop()
        main.step("**************\nPull and build (if necessary) the latest ONOS code from Gerrit \n****************\n")
        uptodate = main.ONOS1.git_pull()
        main.ONOS2.git_pull()
        main.ONOS3.git_pull()
        main.ONOS4.git_pull()
        ver1 = main.ONOS1.get_version()
        ver2 = main.ONOS4.get_version()
        if ver1!=ver2:
            main.ONOS2.git_pull("ONOS1 master")
            main.ONOS3.git_pull("ONOS1 master")
            main.ONOS4.git_pull("ONOS1 master")
        if uptodate==0:
            main.ONOS1.git_compile()
            main.ONOS2.git_compile()
            main.ONOS3.git_compile()
            main.ONOS4.git_compile()
        main.ONOS1.print_version()
        main.step("Start up ZK, RC, and ONOS")
        main.Zookeeper1.start()
        main.Zookeeper2.start()
        main.Zookeeper3.start()
        main.Zookeeper4.start()
        time.sleep(3)
        main.RC1.del_db()
        main.RC2.del_db()
        main.RC3.del_db()
        main.RC4.del_db()
        time.sleep(5)
        main.ONOS1.start_all()
        main.ONOS2.start_all()
        main.ONOS3.start_all()
        main.ONOS4.start_all()
        #main.step("Start Up Mininet")
        main.step("Start up Rest Server")
        main.ONOS1.start_rest()
        main.step("Test startup of Zookeeper")
        for i in range(2):
            zk1up = main.Zookeeper1.isup()
            zk2up = main.Zookeeper2.isup()
            zk3up = main.Zookeeper3.isup()
            zk4up = main.Zookeeper4.isup()
            zkup = zk1up and zk2up and zk3up and zk4up
            if zkup==main.TRUE:
                break
        utilities.assert_equals(expect=main.TRUE,actual=zkup,onpass="Zookeeper is up!",onfail="Zookeeper is down! Exiting!")
        if zkup==main.FALSE:
            main.cleanup()
            main.exit()
        main.step("Test startup of RamCloud")
        for i in range(2):
            rccup = main.RC1.status_coor()
            rcs1up = main.RC1.status_serv()
            rcs2up = main.RC2.status_serv()
            rcs3up = main.RC3.status_serv()
            rcs4up = main.RC4.status_serv()
            rcup = rccup and rcs1up and rcs2up and rcs3up and rcs4up
            if rcup==main.TRUE:
                break
        utilities.assert_equals(expect=main.TRUE,actual=rcup,onpass="RAMCloud is up!",onfail="RAMCloud is down! Exiting!")
        if rcup == main.FALSE:
            main.cleanup()
            main.exit()

        main.step("Test startup of ONOS")
        for i in range(2):
            ONOS1up = main.ONOS1.isup()
            ONOS2up = main.ONOS2.isup()
            ONOS3up = main.ONOS3.isup()
            ONOS4up = main.ONOS4.isup()
            ONOSup = ONOS1up and ONOS2up and ONOS3up and ONOS4up
            if ONOSup==main.TRUE:
                break
        utilities.assert_equals(expect=main.TRUE,actual=ONOSup,onpass="ONOS is up!",onfail="ONOS is down! Exiting!")
        if ONOSup==main.FALSE:
            main.cleanup()
            main.exit()

        main.step("Test startup of Rest Server")
        for i in range(2):
            restStatus = main.ONOS1.rest_status()
            if restStatus==main.TRUE:
                break
        utilities.assert_equals(expect=main.TRUE,actual=restStatus,onpass="Rest Server is up!",onfail="Rest Server is Down! Exiting!")
        if restStatus==main.FALSE:
            main.cleanup()
            main.exit()

        main.step("Test startup of Mininet")
        main.log.report("Host IP Checking using checkIP")
        result1 = main.Mininet1.checkIP(main.params['CASE1']['destination'])
        result2 = main.Mininet1.checkIP(main.params['CASE1']['target'])
        result = result1 and result2
        utilities.assert_equals(expect=main.TRUE,actual=result, onpass="Host IP addresses configured",onfail="Host IP addresses not configured")
        if result==main.FALSE:
            main.cleanup()
            main.exit()




#************************************************************************************************************************************


#************************************************************************************************************************************
        '''
        CASE2: Assign Controllers
        This case will follow the following steps
        1. Assign a Master Controller to each switch
        2. Verify Master Controller
        3. Assign all controllers to all switches
        4. Verify all controllers
        '''
        main.case("Assign Controllers")
        main.step("Assign a master controller to each switch")
        for i in range(25):
            if i<3:
                main.Mininet1.assign_sw_controller(sw=str(i+1),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])
            elif i<5:
                main.Mininet1.assign_sw_controller(sw=str(i+1),ip1=main.params['CTRL']['ip2'],port1=main.params['CTRL']['port2'])
            elif i<16:
                main.Mininet1.assign_sw_controller(sw=str(i+1),ip1=main.params['CTRL']['ip3'],port1=main.params['CTRL']['port3'])
            else:
                main.Mininet1.assign_sw_controller(sw=str(i+1),ip1=main.params['CTRL']['ip4'],port1=main.params['CTRL']['port4'])
        main.step("Verify Master controllers of each switch")
        for i in range(25):
            if i<3:
                
#************************************************************************************************************************************


#************************************************************************************************************************************
        '''
        CASE3: Device Discovery Test
        This case will follow the following steps
        1. Ping to generate arp packets to switch
        2. Find number of hosts with target IP (Try twice if not 1. Then will fail)
        3. Yank the switch
        4. Ping to generate arp packets to switch
        5. Find number of hosts with target IP (Try twice if not 0. Then will fail)
        6. Plug the switch
        7. Ping to generate arp packets to switch
        8. Find number of hosts with target IP (Try twice if not 1. Then will fail)

        
        '''
#************************************************************************************************************************************
