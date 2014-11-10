'''
Topology with 3 core switches connected linearly.

Each 'core' switch has a 'flower' of 10 switches
for a total of 33 switches.

Used in conjunction with 'IntentPerfNext' test
'''

from mininet.topo import Topo

class MyTopo( Topo ):

    def __init__( self ):
        Topo.__init__( self )
       
        #Switches are listed out here for better view
        #of the topology from this code
        core_sw_list = ['s1','s2','s3']
       
        #Flower switches for core switch 1
        flower_sw_list_s1 =\
                ['s10', 's11', 's12', 's13', 's14',
                 's15', 's16', 's17', 's18', 's19']
        #Flower switches for core switch 2
        flower_sw_list_s2 =\
                ['s20', 's21', 's22', 's23', 's24',
                 's25', 's26', 's27', 's28', 's29']
        #Flower switches for core switch 3
        flower_sw_list_s3 =\
                ['s30', 's31', 's32', 's33', 's34',
                 's35', 's36', 's37', 's38', 's39']

        #Store switch objects in these variables
        core_switches = []
        flower_switches_1 = []
        flower_switches_2 = []
        flower_switches_3 = []
       
        #Add switches
        for sw in core_sw_list:
            core_switches.append(
                    self.addSwitch(
                        sw, 
                        dpid = sw.replace('s','').zfill(16)
                    )
            )
        for sw in flower_sw_list_s1:
            flower_switches_1.append(
                    self.addSwitch(
                        sw,
                        dpid = sw.replace('s','').zfill(16)
                    )
            )
        for sw in flower_sw_list_s2:
            flower_switches_2.append(
                    self.addSwitch(
                        sw,
                        dpid = sw.replace('s','').zfill(16)
                    )
            )
        for sw in flower_sw_list_s3:
            flower_switches_3.append(
                    self.addSwitch(
                        sw,
                        dpid = sw.replace('s','').zfill(16)
                    )
            )

        self.addLink(core_switches[0], core_switches[1])
        self.addLink(core_switches[1], core_switches[2])

        for x in range(0, len(flower_sw_list_s1)):
            self.addLink(core_switches[0], flower_switches_1[x]) 
        for x in range(0, len(flower_sw_list_s2)):
            self.addLink(core_switches[1], flower_switches_2[x])
        for x in range(0, len(flower_sw_list_s3)):
            self.addLink(core_switches[2], flower_switches_3[x])

topos = { 'mytopo': ( lambda: MyTopo() ) }
