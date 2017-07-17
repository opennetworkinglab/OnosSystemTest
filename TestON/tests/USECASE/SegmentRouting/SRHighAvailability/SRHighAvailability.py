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

# In this test we perform several failures and then test for connectivity
# CASE1: 2x2 topo + 3 ONOS + | ONOS failure + IP connectivity test | x failures
# CASE2: 2x2 topo + 3 ONOS + | ONOS (random instance) failure + IP connectivity test | x failures
# CASE3: 4x4 topo + 3 ONOS + | ONOS failure + IP connectivity test | x failures
# CASE4: 4x4 topo + 3 ONOS + | ONOS (random instance) failure + IP connectivity test | x failures
# CASE5: 2x2 topo + 3 ONOS + | ONOS failure + Spine failure + IP connectivity test | x failures
# CASE6: 2x2 topo + 3 ONOS + | ONOS (random instance) failure + Spine (random switch) failure + IP connectivity test | x failures
# CASE7: 4x4 topo + 3 ONOS + | ONOS failure + Spine failure + IP connectivity test | x failures
# CASE8: 4x4 topo + 3 ONOS + | ONOS (random instance) failure + Spine (random switch) failure + IP connectivity test | x failures



class SRHighAvailability:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        1) Sets up 3-nodes Onos-cluster
        2) Start 2x2 Leaf-Spine topology
        3) Pingall
        4) Cause sequential ONOS failure
        5) Pingall
        6) Repeat 3), 4), 5) 'failures' times
        """
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
            Testcaselib as run
        if not hasattr( main, 'apps' ):
            run.initTest( main )

        description = "High Availability tests - ONOS failures with 2x2 Leaf-spine "
        main.case( description )
        run.config(main, '2x2', 3)
        run.installOnos( main )
        run.startMininet( main, 'cord_fabric.py' )
        # pre-configured routing and bridging test
        run.checkFlows( main, minFlowCount=116 )
        run.pingAll( main )
        for i in range(0, main.failures):
            toKill = i % main.numCtrls
            run.killOnos( main, [ toKill ], '4', '8', '2' )
            run.pingAll( main, 'CASE1_Failure%d' % (i+1) )
            run.recoverOnos( main, [ toKill ], '4', '8', '3' )
            run.checkFlows( main, minFlowCount=116 )
            run.pingAll( main, 'CASE1_Recovery%d' % (i+1) )
        run.cleanup( main )

    def CASE2( self, main ):
        """
        1) Sets up 3-nodes Onos-cluster
        2) Start 2x2 Leaf-Spine topology
        3) Pingall
        4) Cause random ONOS failure
        5) Pingall
        6) Repeat 3), 4), 5) 'failures' times
        """
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
            Testcaselib as run
        import random
        from random import randint
        from datetime import datetime
        if not hasattr( main, 'apps' ):
            run.initTest( main )

        description = "High Availability tests - ONOS random failures with 2x2 Leaf-spine "
        main.case( description )
        run.config(main, '2x2', 3)
        run.installOnos( main )
        run.startMininet( main, 'cord_fabric.py' )
        # pre-configured routing and bridging test
        run.checkFlows( main, minFlowCount=116 )
        run.pingAll( main )
        random.seed(datetime.now())
        for i in range(0, main.failures):
            toKill = randint(0, (main.numCtrls-1))
            run.killOnos( main, [ toKill ], '4', '8', '2' )
            run.pingAll( main, 'CASE2_Failure%d' % (i+1) )
            run.recoverOnos( main, [ toKill ], '4', '8', '3' )
            run.checkFlows( main, minFlowCount=116 )
            run.pingAll( main, 'CASE2_Recovery%d' % (i+1) )
        run.cleanup( main )

    def CASE3( self, main ):
        """
        1) Sets up 3-nodes Onos-cluster
        2) Start 4x4 Leaf-Spine topology
        3) Pingall
        4) Cause sequential ONOS failure
        5) Pingall
        6) Repeat 3), 4), 5) 'failures' times
        """
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
            Testcaselib as run
        if not hasattr( main, 'apps' ):
            run.initTest( main )

        description = "High Availability tests - ONOS failures with 4x4 Leaf-spine "
        main.case( description )
        run.config(main, '4x4', 3)
        run.installOnos( main )
        run.startMininet( main, 'cord_fabric.py', args="--leaf=4 --spine=4" )
        # pre-configured routing and bridging test
        run.checkFlows( main, minFlowCount=350 )
        run.pingAll( main )
        for i in range(0, main.failures):
            toKill = i % main.numCtrls
            run.killOnos( main, [ toKill ], '8', '32', '2' )
            run.pingAll( main, 'CASE3_Failure%d' % (i+1) )
            run.recoverOnos( main, [ toKill ], '8', '32', '3' )
            run.checkFlows( main, minFlowCount=350 )
            run.pingAll( main, 'CASE3_Recovery%d' % (i+1) )
        run.cleanup( main )

    def CASE4( self, main ):
        """
        1) Sets up 3-nodes Onos-cluster
        2) Start 4x4 Leaf-Spine topology
        3) Pingall
        4) Cause random ONOS failure
        5) Pingall
        6) Repeat 3), 4), 5) 'failures' times
        """
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
            Testcaselib as run
        import random
        from random import randint
        from datetime import datetime
        if not hasattr( main, 'apps' ):
            run.initTest( main )

        description = "High Availability tests - ONOS random failures with 4x4 Leaf-spine "
        main.case( description )
        run.config(main, '4x4', 3)
        run.installOnos( main )
        run.startMininet( main, 'cord_fabric.py', args="--leaf=4 --spine=4" )
        # pre-configured routing and bridging test
        run.checkFlows( main, minFlowCount=350 )
        run.pingAll( main )
        random.seed(datetime.now())
        for i in range(0, main.failures):
            toKill = randint(0, (main.numCtrls-1))
            run.killOnos( main, [ toKill ], '8', '32', '2' )
            run.pingAll( main, 'CASE4_Failure%d' % (i+1) )
            run.recoverOnos( main, [ toKill ], '8', '32', '3' )
            run.checkFlows( main, minFlowCount=350 )
            run.pingAll( main, 'CASE4_Recovery%d' % (i+1) )
        run.cleanup( main )

    def CASE5( self, main ):
        """
        1) Sets up 3-nodes Onos-cluster
        2) Start 2x2 Leaf-Spine topology
        3) Pingall
        4) Cause sequential ONOS failure
        5) Pingall
        6) Cause sequential Spine failure
        7) Pingall
        8) Repeat 3), 4), 5), 6), 7), 'failures' times
        """
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
            Testcaselib as run
        import time
        if not hasattr( main, 'apps' ):
            run.initTest( main )

        description = "High Availability tests - ONOS failures and Switch failures with 2x2 Leaf-spine "
        main.case( description )
        run.config(main, '2x2', 3)
        run.installOnos( main )
        run.startMininet( main, 'cord_fabric.py' )
        # pre-configured routing and bridging test
        run.checkFlows( main, minFlowCount=116 )
        run.pingAll( main )
        for i in range(0, main.failures):
            onosToKill = i % main.numCtrls
            switchToKill = i % len(main.spines)
            run.killOnos( main, [ onosToKill ], '4', '8', '2' )
            run.pingAll( main, 'CASE5_ONOS_Failure%d' % (i+1) )
            run.killSwitch( main, main.spines[switchToKill]['name'], switches='3', links='4' )
            time.sleep( main.switchSleep )
            run.pingAll( main, "CASE5_SWITCH_Failure%d" % (i+1) )
            run.recoverSwitch( main, main.spines[switchToKill]['name'], switches='4', links='8' )
            run.checkFlows( main, minFlowCount=116 )
            run.pingAll( main, "CASE5_SWITCH_Recovery%d" % (i+1) )
            run.recoverOnos( main, [ onosToKill ], '4', '8', '3' )
            run.checkFlows( main, minFlowCount=116 )
            run.pingAll( main, 'CASE5_ONOS_Recovery%d' % (i+1) )
        run.cleanup( main )

    def CASE6( self, main ):
        """
        1) Sets up 3-nodes Onos-cluster
        2) Start 2x2 Leaf-Spine topology
        3) Pingall
        4) Cause random ONOS failure
        5) Pingall
        6) Cause random Spine failure
        7) Pingall
        8) Repeat 3), 4), 5), 6), 7) 'failures' times
        """
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
            Testcaselib as run
        import time
        import random
        from random import randint
        from datetime import datetime
        if not hasattr( main, 'apps' ):
            run.initTest( main )

        description = "High Availability tests - ONOS random failures and Switch random failures with 2x2 Leaf-spine "
        main.case( description )
        run.config(main, '2x2', 3)
        run.installOnos( main )
        run.startMininet( main, 'cord_fabric.py' )
        # pre-configured routing and bridging test
        run.checkFlows( main, minFlowCount=116 )
        run.pingAll( main )
        for i in range(0, main.failures):
            onosToKill = randint(0, (main.numCtrls-1))
            switchToKill = randint(0, 1)
            run.killOnos( main, [ onosToKill ], '4', '8', '2' )
            run.pingAll( main, 'CASE6_ONOS_Failure%d' % (i+1) )
            run.killSwitch( main, main.spines[switchToKill]['name'], switches='3', links='4' )
            time.sleep( main.switchSleep )
            run.pingAll( main, "CASE6_SWITCH_Failure%d" % (i+1) )
            run.recoverSwitch( main, main.spines[switchToKill]['name'], switches='4', links='8' )
            run.checkFlows( main, minFlowCount=116 )
            run.pingAll( main, "CASE6_SWITCH_Recovery%d" % (i+1) )
            run.recoverOnos( main, [ onosToKill ], '4', '8', '3' )
            run.checkFlows( main, minFlowCount=116 )
            run.pingAll( main, 'CASE6_ONOS_Recovery%d' % (i+1) )
        run.cleanup( main )

    def CASE7( self, main ):
        """
        1) Sets up 3-nodes Onos-cluster
        2) Start 4x4 Leaf-Spine topology
        3) Pingall
        4) Cause sequential ONOS failure
        5) Pingall
        6) Cause sequential Spine failure
        7) Pingall
        8) Repeat 3), 4), 5), 6), 7), 'failures' times
        """
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
            Testcaselib as run
        import time
        if not hasattr( main, 'apps' ):
            run.initTest( main )

        description = "High Availability tests - ONOS failures and Switch failures with 4x4 Leaf-spine "
        main.case( description )
        run.config(main, '4x4', 3)
        run.installOnos( main )
        run.startMininet( main, 'cord_fabric.py', args="--leaf=4 --spine=4" )
        # pre-configured routing and bridging test
        run.checkFlows( main, minFlowCount=350 )
        run.pingAll( main )
        for i in range(0, main.failures):
            onosToKill = i % main.numCtrls
            switchToKill = i % len(main.spines)
            run.killOnos( main, [ onosToKill ], '8', '32', '2' )
            run.pingAll( main, 'CASE7_ONOS_Failure%d' % (i+1) )
            run.killSwitch( main, main.spines[switchToKill]['name'], switches='7', links='24' )
            time.sleep( main.switchSleep )
            run.pingAll( main, "CASE7_SWITCH_Failure%d" % (i+1) )
            run.recoverSwitch( main, main.spines[switchToKill]['name'], switches='8', links='32' )
            run.checkFlows( main, minFlowCount=350 )
            run.pingAll( main, "CASE7_SWITCH_Recovery%d" % (i+1) )
            run.recoverOnos( main, [ onosToKill ], '8', '32', '3' )
            run.checkFlows( main, minFlowCount=350 )
            run.pingAll( main, 'CASE7_ONOS_Recovery%d' % (i+1) )
        run.cleanup( main )

    def CASE8( self, main ):
        """
        1) Sets up 3-nodes Onos-cluster
        2) Start 4x4 Leaf-Spine topology
        3) Pingall
        4) Cause random ONOS failure
        5) Pingall
        6) Cause random Spine failure
        7) Pingall
        8) Repeat 3), 4), 5), 6), 7), 'failures' times
        """
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
            Testcaselib as run
        import time
        import random
        from random import randint
        from datetime import datetime
        if not hasattr( main, 'apps' ):
            run.initTest( main )

        description = "High Availability tests - ONOS random failures and Switch random failures with 4x4 Leaf-spine "
        main.case( description )
        run.config(main, '4x4', 3)
        run.installOnos( main )
        run.startMininet( main, 'cord_fabric.py', args="--leaf=4 --spine=4" )
        # pre-configured routing and bridging test
        run.checkFlows( main, minFlowCount=350 )
        run.pingAll( main )
        for i in range(0, main.failures):
            onosToKill = randint(0, (main.numCtrls-1))
            switchToKill = randint(0, 3)
            run.killOnos( main, [ onosToKill ], '8', '32', '2' )
            run.pingAll( main, 'CASE8_ONOS_Failure%d' % (i+1) )
            run.killSwitch( main, main.spines[switchToKill]['name'], switches='7', links='24' )
            time.sleep( main.switchSleep )
            run.pingAll( main, "CASE8_SWITCH_Failure%d" % (i+1) )
            run.recoverSwitch( main, main.spines[switchToKill]['name'], switches='8', links='32' )
            run.checkFlows( main, minFlowCount=350 )
            run.pingAll( main, "CASE8_SWITCH_Recovery%d" % (i+1) )
            run.recoverOnos( main, [ onosToKill ], '8', '32', '3' )
            run.checkFlows( main, minFlowCount=350 )
            run.pingAll( main, 'CASE8_ONOS_Recovery%d' % (i+1) )
        run.cleanup( main )
