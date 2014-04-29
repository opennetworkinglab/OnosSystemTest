"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo

class MyTopo( Topo ):
	"Simple topology example."

	def __init__( self ):
		"Create custom topo."
		# Initialize topology
		Topo.__init__( self )

		# Make the middle triangle	
		leftSwitch = self.addSwitch( 's1' , dpid = '1000'.zfill(16))
		rightSwitch = self.addSwitch( 's2' , dpid = '2000'.zfill(16))
		topSwitch = self.addSwitch( 's3' , dpid = '3000'.zfill(16))
		lefthost = self.addHost( 'h1' )
		righthost = self.addHost( 'h2' )
		tophost = self.addHost( 'h3' )
		self.addLink( leftSwitch, lefthost )
		self.addLink( rightSwitch, righthost )
		self.addLink( topSwitch, tophost )

		self.addLink( leftSwitch, rightSwitch )
		self.addLink( leftSwitch, topSwitch )
		self.addLink( topSwitch, rightSwitch )

		# Make aggregation switches
		agg1Switch = self.addSwitch( 's4', dpid = '1004'.zfill(16) ) 
		agg2Switch = self.addSwitch( 's5', dpid = '2005'.zfill(16) ) 
		agg1Host = self.addHost( 'h4' ) 
		agg2Host = self.addHost( 'h5' ) 

		self.addLink( agg1Switch, agg1Host, port1=1, port2=1 )
		self.addLink( agg2Switch, agg2Host, port1=1, port2=1 )

		self.addLink( agg2Switch, rightSwitch )
		self.addLink( agg1Switch, leftSwitch )

		# Make two aggregation fans
		for i in range(10):
			num=str(i+6)
			switch = self.addSwitch( 's' + num, dpid = ('10' + num.zfill(2) ).zfill(16))
			host = self.addHost( 'h' + num ) 
			self.addLink( switch, host, port1=1, port2=1 ) 
			self.addLink( switch, agg1Switch ) 

		for i in range(10):
			num=str(i+31)
			switch = self.addSwitch( 's' + num, dpid = ('20' + num.zfill(2)).zfill(16) )
			host = self.addHost( 'h' + num ) 
			self.addLink( switch, host, port1=1, port2=1 ) 
			self.addLink( switch, agg2Switch ) 

topos = { 'mytopo': ( lambda: MyTopo() ) }
