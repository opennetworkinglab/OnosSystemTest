"""
Copyright 2017 Open Networking Foundation ( ONF )

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    ( at your option ) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.
"""

from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as run
import random
from random import randint
from datetime import datetime
import time

class SRHAFuncs():

    def __init__( self ):
        self.default = ''
        self.topo = dict()
        self.topo[ '2x2' ] = ( 2, 2, '', '2x2 Leaf-spine' )
        self.topo[ '4x4' ] = ( 4, 4, '--leaf=4 --spine=4', '4x4 Leaf-spine' )

    def runTest( self, main, caseNum, numNodes, Topo, minFlow, isRandom, isKillingSwitch ):
        try:
            if not hasattr( main, 'apps' ):
                run.initTest( main )

            description = "High Availability tests - " + \
                          self.generateDescription( isRandom, isKillingSwitch ) + \
                          self.topo[ Topo ][ 3 ]
            main.case( description )
            run.config( main, Topo )
            run.installOnos( main )
            if not main.persistentSetup:
                run.loadJson( main )
            run.loadChart( main )
            run.startMininet( main, 'cord_fabric.py', args=self.topo[ Topo ][ 2 ] )
            if not main.persistentSetup:
                # xconnects need to be loaded after topology
                run.loadXconnects( main )
            # pre-configured routing and bridging test
            run.checkFlows( main, minFlowCount=minFlow )
            run.pingAll( main )
            switch = self.topo[ Topo ][ 0 ] + self.topo[ Topo ][ 1 ]
            link = ( self.topo[ Topo ][ 0 ] + self.topo[ Topo ][ 1 ] ) * self.topo[ Topo ][ 0 ]
            self.generateRandom( isRandom )
            for i in range( 0, main.failures ):
                toKill = self.getNextNum( isRandom, main.Cluster.numCtrls, i )
                run.killOnos( main, [ toKill ], '{}'.format( switch ),
                              '{}'.format( link ), '{}'.format( numNodes - 1 ) )
                run.pingAll( main, 'CASE{}_ONOS_Failure{}'.format( caseNum, i + 1 ) )
                if isKillingSwitch:
                    self.killAndRecoverSwitch( main, caseNum, numNodes,
                                               Topo, minFlow, isRandom,
                                               i, switch, link )
                run.recoverOnos( main, [ toKill ], '{}'.format( switch ),
                                 '{}'.format( link ), '{}'.format( numNodes ) )
                run.checkFlows( main, minFlowCount=minFlow,
                                tag='CASE{}_ONOS{}_Recovery'.format( caseNum, i + 1 ) )
                run.pingAll( main, 'CASE{}_ONOS_Recovery{}'.format( caseNum, i + 1 ) )
            # TODO Dynamic config of hosts in subnet
            # TODO Dynamic config of host not in subnet
            # TODO Dynamic config of vlan xconnect
            # TODO Vrouter integration
            # TODO Mcast integration
        except Exception as e:
            main.log.exception( "Error in runTest" )
            main.skipCase( result="FAIL", msg=e )
        finally:
            run.cleanup( main )

    def generateDescription( self, isRandom, isKillingSwitch ):
        return "ONOS " + ( "random " if isRandom else "" ) + "failures" +\
               ( " and Switch " + ( "random " if isRandom else "" ) + "failures "
                 if isKillingSwitch else " " )

    def generateRandom( self, isRandom ):
        if isRandom:
            random.seed( datetime.now() )

    def getNextNum( self, isRandom, numCtrl, pos ):
        return randint( 0, ( numCtrl - 1 ) ) if isRandom else pos % numCtrl

    def killAndRecoverSwitch( self, main, caseNum, numNodes, Topo, minFlow, isRandom, pos, numSwitch, numLink ):
        switchToKill = self.getNextNum( isRandom, self.topo[ Topo ][ 0 ], pos )
        run.killSwitch( main, main.spines[ switchToKill ][ 'name' ],
                        switches='{}'.format( numSwitch - 1 ),
                        links='{}'.format( numLink - numSwitch ) )
        time.sleep( main.switchSleep )
        run.pingAll( main, "CASE{}_SWITCH_Failure{}".format( caseNum, pos + 1 ) )
        run.recoverSwitch( main, main.spines[ switchToKill ][ 'name' ],
                           switches='{}'.format( numSwitch ),
                           links='{}'.format( numLink ) )
        run.checkFlows( main, minFlowCount=minFlow,
                        tag="CASE{}_SWITCH_Recovery{}".format( caseNum, pos + 1 ) )
        run.pingAll( main, "CASE{}_SWITCH_Recovery{}".format( caseNum, pos + 1 ) )
