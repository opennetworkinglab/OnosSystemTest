class NEC:

    def __init__( self ):
        self.prompt = '(.*)'
        self.timeout = 60

    def show( self, *options, **def_args ):
        "Possible Options :['  access-filter  ', '  accounting  ', '  acknowledgments  ', '  auto-config  ', '  axrp  ', '  cfm  ', '  channel-group  ', '  clock  ', '  config-lock-status  ', '  cpu  ', '  dhcp  ', '  dot1x  ', '  dumpfile  ', '  efmoam  ', '  environment  ', '  file  ', '  flash  ', '  gsrp  ', '  history  ', '  igmp-snooping  ', '  interfaces  ', '  ip  ', '  ip-dual  ', '  ipv6-dhcp  ', '  license  ', '  lldp  ', '  logging  ', '  loop-detection  ', '  mac-address-table  ', '  mc  ', '  memory  ', '  mld-snooping  ', '  netconf  ', '  netstat  ', '  ntp  ', '  oadp  ', '  openflow  ', '  port  ', '  power  ', '  processes  ', '  qos  ', '  qos-flow  ', '  sessions  ', '  sflow  ', '  spanning-tree  ', '  ssh  ', '  system  ', '  tcpdump  ', '  tech-support  ', '  track  ', '  version  ', '  vlan  ', '  vrrpstatus  ', '  whoami  ']"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute( cmd="show " + arguments, prompt=prompt, timeout=timeout )
        return main.TRUE

    def show_ip( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   ip   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_mc( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   mc   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_cfm( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   cfm   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_ntp( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   ntp   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_ssh( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   ssh   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_qos( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   qos   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_cpu( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   cpu   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_vlan( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   vlan   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_lldp( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   lldp   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_dhcp( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   dhcp   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_axrp( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   axrp   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_oadp( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   oadp   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_gsrp( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   gsrp   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_port( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   port   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_file( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   file   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_power( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   power   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_clock( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   clock   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_dot1x( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   dot1x   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_sflow( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   sflow   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_track( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   track   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_flash( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   flash   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_system( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   system   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_whoami( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   whoami   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_efmoam( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   efmoam   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_memory( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   memory   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_tcpdump( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   tcpdump   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_history( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   history   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_logging( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   logging   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_license( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   license   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_netstat( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   netstat   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_version( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   version   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_netconf( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   netconf   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_ipdual( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   ip-dual   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_sessions( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   sessions   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_qosflow( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   qos-flow   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_openflow( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   openflow   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_dumpfile( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   dumpfile   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_ipv6dhcp( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   ipv6-dhcp   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_processes( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   processes   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_vrrpstatus( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   vrrpstatus   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_interfaces( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   interfaces   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_environment( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   environment   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_autoconfig( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   auto-config   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_techsupport( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   tech-support   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_mldsnooping( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   mld-snooping   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_igmpsnooping( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   igmp-snooping   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_channelgroup( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   channel-group   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_spanningtree( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   spanning-tree   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_loopdetection( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   loop-detection   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_acknowledgments( self, *options, **def_args ):
        "Possible Options :['  interface  ']"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   acknowledgments   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_macaddresstable( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   mac-address-table   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_configlockstatus( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   config-lock-status   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE

    def show_acknowledgments_interface( self, *options, **def_args ):
        "Possible Options :[]"
        arguments = ''
        for option in options:
            arguments = arguments + option + ' '
        prompt = def_args.setdefault( 'prompt', self.prompt )
        timeout = def_args.setdefault( 'timeout', self.timeout )
        self.execute(
            cmd="show   acknowledgments     interface   " +
            arguments,
            prompt=prompt,
            timeout=timeout )
        return main.TRUE
