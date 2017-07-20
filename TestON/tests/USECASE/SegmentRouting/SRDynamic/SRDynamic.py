"""
Copyright 2016 Open Networking Foundation (ONF)

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

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
"""

# CASE1: 2x2 Leaf-Spine topo and test IP connectivity
# CASE2: 4x4 topo + IP connectivity test
# CASE3: Single switch topo + IP connectivity test
# CASE4: 2x2 topo + 3-node ONOS CLUSTER + IP connectivity test
# CASE5: 4x4 topo + 3-node ONOS CLUSTER + IP connectivity test
# CASE6: Single switch + 3-node ONOS CLUSTER + IP connectivity test

class SRDynamic:
    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        Sets up 1-node Onos-cluster
        Start 2x2 Leaf-Spine topology
        Pingall
        """
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
            Testcaselib as run
        if not hasattr( main, 'apps' ):
            run.initTest( main )

        description = "Bridging and Routing sanity test with 2x2 Leaf-spine "
        main.case( description )

        main.cfgName = '2x2'
        main.Cluster.setRunningNode( 1 )
        run.installOnos( main, vlanCfg=False )
        run.startMininet( main, 'cord_fabric.py' )
        # pre-configured routing and bridging test
        run.checkFlows( main, minFlowCount=116 )
        run.pingAll( main, dumpflows=False, )
        run.addHostCfg( main )
        run.checkFlows( main, minFlowCount=140, dumpflows=False )
        run.pingAll( main, "CASE1" )
        run.cleanup( main )

    def CASE2( self, main ):
        """
        Sets up 1-node Onos-cluster
        Start 4x4 Leaf-Spine topology
        Pingall
        """
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
            Testcaselib as run
        if not hasattr( main, 'apps' ):
            run.initTest( main )
        description = "Bridging and Routing sanity test with 4x4 Leaf-spine "
        main.case( description )
        main.cfgName = '4x4'
        main.Cluster.setRunningNode( 1 )
        run.installOnos( main, vlanCfg=False )
        run.startMininet( main, 'cord_fabric.py',
                          args="--leaf=4 --spine=4" )
        # pre-configured routing and bridging test
        run.checkFlows( main, minFlowCount=350 )
        run.pingAll( main, dumpflows=False )
        run.addHostCfg( main )
        run.checkFlows( main, minFlowCount=380, dumpflows=False )
        run.pingAll( main, 'CASE2' )
        run.cleanup( main )

    def CASE3( self, main ):
        """
        Sets up 1-node Onos-cluster
        Start single switch topology
        Pingall
        """
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
            Testcaselib as run
        if not hasattr( main, 'apps' ):
            run.initTest( main )
        description = "Bridging and Routing sanity test with single switch "
        main.case( description )
        main.cfgName = '0x1'
        main.Cluster.setRunningNode( 1 )
        run.installOnos( main, vlanCfg=False )
        run.startMininet( main, 'cord_fabric.py',
                          args="--leaf=1 --spine=0" )
        # pre-configured routing and bridging test
        run.checkFlows( main, minFlowCount=15 )
        run.pingAll( main, dumpflows=False )
        run.addHostCfg( main )
        run.checkFlows( main, minFlowCount=18, dumpflows=False )
        run.pingAll( main, 'CASE3' )
        run.cleanup( main )

    def CASE4( self, main ):
        """
        Sets up 3-node Onos-cluster
        Start 2x2 Leaf-Spine topology
        Pingall
        """
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
            Testcaselib as run
        if not hasattr( main, 'apps' ):
            run.initTest( main )
        description = "Bridging and Routing sanity test with 2x2 Leaf-spine "
        main.case( description )

        main.cfgName = '2x2'
        main.Cluster.setRunningNode( 3 )
        run.installOnos( main, vlanCfg=False )
        run.startMininet( main, 'cord_fabric.py' )
        # pre-configured routing and bridging test
        run.checkFlows( main, minFlowCount=116 )
        run.pingAll( main, dumpflows=False )
        run.addHostCfg( main )
        run.checkFlows( main, minFlowCount=140, dumpflows=False )
        run.pingAll( main, "CASE4" )
        run.killOnos( main, [ 0 ], '4', '8', '2' )
        run.delHostCfg( main )
        run.checkFlows( main, minFlowCount=116, dumpflows=False )
        run.pingAll( main, "CASE4_after" )
        run.cleanup( main )

    def CASE5( self, main ):
        """
        Sets up 3-node Onos-cluster
        Start 4x4 Leaf-Spine topology
        Pingall
        """
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
            Testcaselib as run
        if not hasattr( main, 'apps' ):
            run.initTest( main )
        description = "Bridging and Routing sanity test with 4x4 Leaf-spine "
        main.case( description )
        main.cfgName = '4x4'
        main.Cluster.setRunningNode( 3 )
        run.installOnos( main, vlanCfg=False )
        run.startMininet( main, 'cord_fabric.py',
                          args="--leaf=4 --spine=4" )
        # pre-configured routing and bridging test
        run.checkFlows( main, minFlowCount=350 )
        run.pingAll( main, dumpflows=False )
        run.addHostCfg( main )
        run.checkFlows( main, minFlowCount=380, dumpflows=False )
        run.pingAll( main, 'CASE5' )
        run.killOnos( main, [ 0 ], '8', '32', '2' )
        run.delHostCfg( main )
        run.checkFlows( main, minFlowCount=350, dumpflows=False )
        run.pingAll( main, "CASE5_After" )
        run.cleanup( main )

    def CASE6( self, main ):
        """
        Sets up 3-node Onos-cluster
        Start single switch topology
        Pingall
        """
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
            Testcaselib as run
        if not hasattr( main, 'apps' ):
            run.initTest( main )
        description = "Bridging and Routing sanity test with single switch "
        main.case( description )
        main.cfgName = '0x1'
        main.Cluster.setRunningNode( 3 )
        run.installOnos( main, vlanCfg=False )
        run.startMininet( main, 'cord_fabric.py',
                          args="--leaf=1 --spine=0" )
        # pre-configured routing and bridging test
        run.checkFlows( main, minFlowCount=15 )
        run.pingAll( main, dumpflows=False )
        run.addHostCfg( main )
        run.checkFlows( main, minFlowCount=20, dumpflows=False )
        run.pingAll( main, 'CASE6' )
        run.killOnos( main, [ 0 ], '1', '0', '2' )
        run.delHostCfg( main )
        run.checkFlows( main, minFlowCount=15, dumpflows=False )
        run.pingAll( main, "CASE6_After" )
        run.cleanup( main )
