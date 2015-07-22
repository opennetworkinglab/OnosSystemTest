"""
Driver for blank dataplane VMs. Created for SDNIP test.
"""
import pexpect
from drivers.common.clidriver import CLI


class DPCliDriver( CLI ):

    def __init__( self ):
        super( CLI, self ).__init__()

    def connect( self, **connectargs ):
        for key in connectargs:
            vars( self )[ key ] = connectargs[ key ]

        self.name = self.options[ 'name' ]
        self.handle = super( DPCliDriver, self ).connect( user_name=self.user_name,
                        ip_address=self.ip_address,
                        port=self.port,
                        pwd=self.pwd )

        if self.handle:
            return self.handle
        else:
            main.log.info( "NO HANDLE" )
            return main.FALSE

    def create_interfaces( self, net, number, start ):
        """
        Creates a number,specified by 'number,' of subinterfaces on eth0.
        Ip addresses start at 'net'.'start'.1.1 with a 24 bit netmask.
        Addresses increment sequentially in the third quad, therefore all
        interfaces are in different subnets on the same machine. When the
        third quad reaches 255, it is reset to 1 and the second quad is
        incremented. Every single ip address is placed in a file in /tmp
        titled 'ip_table{net}.txt'. The file is used by 'pingall_interfaces()'
        as a fping argument

        This method returns true if all interfaces are created without a hitch,
        and false if a single interface has issues
        """
        self.handle.sendline( "" )
        self.handle.expect( "\$" )

        self.handle.sendline( "rm /tmp/local_ip.txt" )
        self.handle.expect( "\$" )
        self.handle.sendline( "touch /tmp/local_ip.txt" )
        self.handle.expect( "\$" )

        main.log.info( "Creating interfaces" )
        k = 0
        intf = 0
        while number != 0:
            k = k + 1
            if k == 256:
                k = 1
                start = start + 1
            number = number - 1
            intf = intf + 1
            ip = net + "." + str( start ) + "." + str( k ) + ".1"
            self.handle.sendline(
                "sudo ifconfig eth0:" + str(
                    intf ) + " " + ip + " netmask 255.255.255.0" )

            i = self.handle.expect( [
                                    "\$",
                                    "password",
                                    pexpect.TIMEOUT,
                                    pexpect.EOF ],
                                    timeout=120 )

            if i == 0:
                self.handle.sendline(
                    "echo " + str( ip ) + " >> /tmp/local_ip.txt" )
                self.handle.expect( "\$" )
            elif i == 1:
                main.log.info( "Sending sudo password" )
                self.handle.sendline( self.pwd )
                self.handle.expect( "\$" )
            else:
                main.log.error( "INTERFACES NOT CREATED" )
                return main.FALSE

    def pingall_interfaces( self, netsrc, netstrt, netdst, destlogin, destip ):
        """
        Copies the /tmp/ip_table{ net }.txt file from the machine you wish to
        ping, then runs fping with a source address of
        { netsrc }.{ netstrt }.1.1 on the copied file.
        Check every single response for reachable or unreachable. If all are
        reachable, function returns true. If a SINGLE host is unreachable,
        then the function stops and returns false. If fping is not installed,
        this function will install fping then run the same command
        """
        self.handle.sendline( "" )
        self.handle.expect( "\$" )

        self.handle.sendline( "scp " + str( destlogin ) + "@" +
                              str( destip ) +
                              ":/tmp/local_ip.txt /tmp/ip_table" +
                              str( netsrc ) + ".txt" )

        i = self.handle.expect( [
                                "100%",
                                "password",
                                pexpect.TIMEOUT ],
                                timeout=30 )

        if i == 0:
            main.log.info( "Copied ping file successfully" )
        elif i == 1:
            self.handle.sendline( self.pwd )
            self.handle.expect( "100%" )
            main.log.info( "Copied ping file successfully" )
        elif i == 2:
            main.log.error( "COULD NOT COPY PING FILE FROM " + str( destip ) )
            result = main.FALSE
            return result

        self.handle.sendline( "" )
        self.handle.expect( "\$" )

        main.log.info( "Pinging interfaces on the " + str( netdst ) +
                       " network from " + str( netsrc ) + "." +
                       str( netstrt ) + ".1.1" )
        self.handle.sendline( "sudo fping -S " + str( netsrc ) + "." +
                              str( netstrt ) + ".1.1 -f /tmp/ip_table" +
                              str( netdst ) + ".txt" )
        while 1:
            i = self.handle.expect( [
                                    "reachable",
                                    "unreachable",
                                    "\$",
                                    "password",
                                    pexpect.TIMEOUT,
                                    "not installed" ],
                                    timeout=45 )
            if i == 0:
                result = main.TRUE
            elif i == 1:
                main.log.error( "An interface was unreachable" )
                result = main.FALSE
                return result
            elif i == 2:
                main.log.info( "All interfaces reachable" )
                result = main.FALSE
                return result
            elif i == 3:
                self.handle.sendline( self.pwd )
            elif i == 4:
                main.log.error( "Unable to fping" )
                result = main.FALSE
                return result
            elif i == 5:
                main.log.info( "fping not installed, installing fping" )
                self.handle.sendline( "sudo apt-get install fping" )
                i = self.handle.expect( [ "password",
                                          "\$",
                                          pexpect.TIMEOUT ],
                                        timeout=60 )
                if i == 0:
                    self.handle.sendline( self.pwd )
                    self.handle.expect( "\$", timeout=30 )
                    main.log.info( "fping installed, now pinging interfaces" )
                    self.handle.sendline(
                        "sudo fping -S " + str(
                            netsrc ) + "." + str(
                                netstrt ) + ".1.1 -f /tmp/ip_table" + str(
                                    netdst ) + ".txt" )
                elif i == 1:
                    main.log.info( "fping installed, now pinging interfaces" )
                    self.handle.sendline(
                        "sudo fping -S " + str(
                            netsrc ) + "." + str(
                                netstrt ) + ".1.1 -f /tmp/ip_table" + str(
                                    netdst ) + ".txt" )
                elif i == 2:
                    main.log.error( "Could not install fping" )
                    result = main.FALSE
                    return result

    def disconnect( self ):
        response = ''
        try:
            self.handle.sendline( "exit" )
            self.handle.expect( "closed" )
        except pexpect.ExceptionPexpect:
            main.log.exception( "Connection failed to the host" )
            response = main.FALSE
        return response

