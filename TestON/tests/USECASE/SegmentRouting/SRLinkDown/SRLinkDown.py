# This test should always succeed. it runs cases 1,2,3,4
#CASE1: Get and Build ONOS
#CASE2: Package and Install ONOS
#CASE3: Start Mininet and check flows
#CASE4: Ping all
#CASE5: Link Failure
#CASE6: Switch Failure
#CASE7: ONOS Failure
#CASE8: CLUSTER Failure
#CASE10: Logging

class SRLinkDown:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        Sets up 1-node Onos-cluster
        Start 2x2 Leaf-Spine topology
        Pingall
        """
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as run
        if not hasattr(main,'apps'):
            run.initTest(main)

        description = "Bridging and Routing sanity test with 2x2 Leaf-spine "
        main.case( description )

        main.cfgName = '2x2'
        main.numCtrls = 1
        run.installOnos(main)
        run.startMininet(main, 'cord_fabric.py')
        #pre-configured routing and bridging test
        run.checkFlows(main, flowCount=116)
        run.pingAll(main)
        run.killLink(main, 'spine101', 'leaf2', switches='4', links='6')
        run.pingAll(main, "CASE1_AfterLinkDown")
        run.restoreLink(main, 'spine101', 'leaf2','of:0000000000000101',
                        'of:0000000000000002', '2', '1', '4', '8')
        run.pingAll(main, "CASE1_AfterLinkUp")
        #TODO Dynamic config of hosts in subnet
        #TODO Dynamic config of host not in subnet
        #TODO Dynamic config of vlan xconnect
        #TODO Vrouter integration
        #TODO Mcast integration
        run.cleanup(main)

    def CASE2( self, main ):
        """
        Sets up 1-node Onos-cluster
        Start 4x4 Leaf-Spine topology
        Pingall
        """
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as run
        if not hasattr(main,'apps'):
            run.initTest(main)
        description = "Bridging and Routing sanity test with 4x4 Leaf-spine "
        main.case( description )
        main.cfgName = '4x4'
        main.numCtrls = 1
        run.installOnos(main)
        run.startMininet(main, 'cord_fabric.py', args="--leaf=4 --spine=4")
        #pre-configured routing and bridging test
        run.checkFlows(main, flowCount=350)
        run.pingAll(main)
        run.killLink(main, 'spine101', 'leaf2', switches='8', links='30')
        run.pingAll(main, "CASE2_AfterLinkDown")
        run.restoreLink(main, 'spine101', 'leaf2','of:0000000000000101',
                    'of:0000000000000002', '2', '1', '8', '32')
        run.pingAll(main, "CASE2_AfterLinkUp")
        #TODO Dynamic config of hosts in subnet
        #TODO Dynamic config of host not in subnet
        #TODO preconfigured xconnect
        #TODO Vrouter integration
        #TODO Mcast integration
        run.cleanup(main)

    def CASE3( self, main ):
        """
        Sets up 3-node Onos-cluster
        Start 2x2 Leaf-Spine topology
        Pingall
        """
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as run
        if not hasattr(main,'apps'):
            run.initTest(main)
        description = "Bridging and Routing sanity test with 2x2 Leaf-spine "
        main.case( description )
        main.cfgName = '2x2'
        main.numCtrls = 3
        run.installOnos(main)
        run.startMininet(main, 'cord_fabric.py')
        #pre-configured routing and bridging test
        run.checkFlows(main, flowCount=116)
        run.pingAll(main)
        run.killLink(main, 'spine101', 'leaf2', switches='4', links='6')
        run.pingAll(main, "CASE3_AfterLinkDown")
        run.restoreLink(main, 'spine101', 'leaf2','of:0000000000000101',
                        'of:0000000000000002', '2', '1', '4', '8')
        run.pingAll(main, "CASE3_AfterLinkUp")
        #TODO Dynamic config of hosts in subnet
        #TODO Dynamic config of host not in subnet
        #TODO Dynamic config of vlan xconnect
        #TODO Vrouter integration
        #TODO Mcast integration
        run.cleanup(main)