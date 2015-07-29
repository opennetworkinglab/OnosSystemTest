'''

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


'''
class Vyatta:
    def __init__( self ):
        self.prompt = '(.*)'
        self.timeout = 60

    def show_interfaces(self, *options, **def_args ):
        '''Possible Options :['ethernet', 'loopback']'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "show interfaces "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet(self, *options, **def_args ):
        '''Possible Options :['eth0', 'eth1']'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def show_interfaces_loopback(self, *options, **def_args ):
        '''Possible Options :['lo']'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "show interfaces loopback "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def show_interfaces_ethernet(self, *options, **def_args ):
        '''Possible Options :['eth0', 'eth1']'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "show interfaces ethernet "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def show_interfaces_loopback_lo(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "show interfaces loopback lo "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0(self, *options, **def_args ):
        '''Possible Options :['address', 'bond-group', 'bridge-group', 'description', 'dhcpv6-options', 'DHCPv6', 'disable', 'disable-flow-control', 'Disable', 'disable-link-detect', 'Ignore', 'duplex', 'firewall', 'hw-id', 'ip', 'ipv6', 'mac', 'mirror', 'mtu', 'policy', 'pppoe']'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def show_interfaces_ethernet_eth1(self, *options, **def_args ):
        '''Possible Options :['address', 'duplex', 'hw-id', 'smp_affinity', 'speed']'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "show interfaces ethernet eth1 "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def show_interfaces_ethernet_eth0(self, *options, **def_args ):
        '''Possible Options :['duplex', 'hw-id', 'smp_affinity', 'speed']'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "show interfaces ethernet eth0 "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_ip(self, *options, **def_args ):
        '''Possible Options :['enable-proxy-arp', 'Enable', 'ospf', 'rip']'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 ip "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_hwid(self, *options, **def_args ):
        '''Possible Options :['Media']'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 hw-id "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_DHCPv6(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 DHCPv6 "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_duplex(self, *options, **def_args ):
        '''Possible Options :['auto', 'half', 'full']'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 duplex "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def show_interfaces_ethernet_eth1_hwid(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "show interfaces ethernet eth1 hw-id "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def show_interfaces_ethernet_eth0_speed(self, *options, **def_args ):
        '''Possible Options :['auto']'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "show interfaces ethernet eth0 speed "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def show_interfaces_ethernet_eth1_speed(self, *options, **def_args ):
        '''Possible Options :['auto']'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "show interfaces ethernet eth1 speed "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def show_interfaces_ethernet_eth0_hwid(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "show interfaces ethernet eth0 hw-id "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_Ignore(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 Ignore "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def show_interfaces_ethernet_eth1_duplex(self, *options, **def_args ):
        '''Possible Options :['auto']'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "show interfaces ethernet eth1 duplex "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def show_interfaces_ethernet_eth0_duplex(self, *options, **def_args ):
        '''Possible Options :['auto']'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "show interfaces ethernet eth0 duplex "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_ip_ospf(self, *options, **def_args ):
        '''Possible Options :['authentication', 'OSPF', 'bandwidth', 'cost', 'dead-interval', 'Interval', 'hello-interval', 'Interval', 'mtu-ignore', 'network', 'priority', 'retransmit-interval', 'Interval', 'transmit-delay', 'Link']'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 ip ospf "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_Disable(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 Disable "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_disable(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 disable "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_address(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 address "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_firewall(self, *options, **def_args ):
        '''Possible Options :['in', 'local', 'out']'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 firewall "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def show_interfaces_ethernet_eth1_address(self, *options, **def_args ):
        '''Possible Options :['192.168.56.81/24']'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "show interfaces ethernet eth1 address "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_ip_Enable(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 ip Enable "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_bondgroup(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 bond-group "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_duplex_half(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 duplex half "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_firewall_in(self, *options, **def_args ):
        '''Possible Options :['ipv6-name', 'name']'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 firewall in "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def show_interfaces_ethernet_eth1_speed_auto(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "show interfaces ethernet eth1 speed auto "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_description(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 description "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def show_interfaces_ethernet_eth0_speed_auto(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "show interfaces ethernet eth0 speed auto "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_hwid_Media(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 hw-id Media "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_duplex_auto(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 duplex auto "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_duplex_full(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 duplex full "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def show_interfaces_ethernet_eth0_duplex_auto(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "show interfaces ethernet eth0 duplex auto "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_ip_ospf_OSPF(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 ip ospf OSPF "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_firewall_out(self, *options, **def_args ):
        '''Possible Options :['ipv6-name', 'name']'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 firewall out "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_bridgegroup(self, *options, **def_args ):
        '''Possible Options :['bridge', 'cost', 'priority']'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 bridge-group "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def show_interfaces_ethernet_eth1_duplex_auto(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "show interfaces ethernet eth1 duplex auto "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_ip_ospf_cost(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 ip ospf cost "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def show_interfaces_ethernet_eth0_smp_affinity(self, *options, **def_args ):
        '''Possible Options :['auto']'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "show interfaces ethernet eth0 smp_affinity "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def show_interfaces_ethernet_eth1_smp_affinity(self, *options, **def_args ):
        '''Possible Options :['auto']'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "show interfaces ethernet eth1 smp_affinity "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_firewall_local(self, *options, **def_args ):
        '''Possible Options :['ipv6-name', 'name']'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 firewall local "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_dhcpv6options(self, *options, **def_args ):
        '''Possible Options :['parameters-only', 'Acquire', 'temporary']'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 dhcpv6-options "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_firewall_in_name(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 firewall in name "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_bridgegroup_cost(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 bridge-group cost "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_firewall_out_name(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 firewall out name "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_ip_ospf_bandwidth(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 ip ospf bandwidth "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def show_interfaces_ethernet_eth0_smp_affinity_auto(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "show interfaces ethernet eth0 smp_affinity auto "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def show_interfaces_ethernet_eth1_smp_affinity_auto(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "show interfaces ethernet eth1 smp_affinity auto "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_ip_enableproxyarp(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 ip enable-proxy-arp "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_disablelinkdetect(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 disable-link-detect "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_firewall_local_name(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 firewall local name "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_bridgegroup_bridge(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 bridge-group bridge "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_disableflowcontrol(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 disable-flow-control "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_bridgegroup_priority(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 bridge-group priority "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_firewall_in_ipv6name(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 firewall in ipv6-name "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_dhcpv6options_Acquire(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 dhcpv6-options Acquire "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_firewall_out_ipv6name(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 firewall out ipv6-name "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_ip_ospf_authentication(self, *options, **def_args ):
        '''Possible Options :['md5', 'plaintext-password', 'Plain']'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 ip ospf authentication "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_firewall_local_ipv6name(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 firewall local ipv6-name "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_dhcpv6options_temporary(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 dhcpv6-options temporary "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_ip_ospf_authentication_md5(self, *options, **def_args ):
        '''Possible Options :['key-id']'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 ip ospf authentication md5 "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_ip_ospf_authentication_Plain(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 ip ospf authentication Plain "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_dhcpv6options_parametersonly(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 dhcpv6-options parameters-only "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_ip_ospf_authentication_md5_keyid(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 ip ospf authentication md5 key-id "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

    def set_interfaces_ethernet_eth0_ip_ospf_authentication_plaintextpassword(self, *options, **def_args ):
        '''Possible Options :[]'''
        arguments= ''
        for option in options:
            arguments = arguments + option +' '
        prompt = def_args.setdefault('prompt',self.prompt)
        timeout = def_args.setdefault('timeout',self.timeout)
        self.execute( cmd= "set interfaces ethernet eth0 ip ospf authentication plaintext-password "+ arguments, prompt = prompt, timeout = timeout )
        return main.TRUE

