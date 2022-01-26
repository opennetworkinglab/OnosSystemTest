"""
Copyright 2022 Open Networking Foundation (ONF)

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

"""

import pexpect
import os
from drivers.common.clidriver import CLI


class MockSMFDriver( CLI ):
    """
    Runs commands using the mock smf program to send messages to a UPF.

    """

    def __init__( self ):
        """
        Initialize client
        """
        super( MockSMFDriver, self ).__init__()
        self.name = None
        self.handle = None
        self.prompt = "\$"
        self.mock_smf_path = None

    def connect( self, **connectargs ):
        """
        Creates the ssh handle for the mock smf
        """
        try:
            for key in connectargs:
                vars( self )[ key ] = connectargs[ key ]
            self.name = self.options.get( "name", "" )
            self.mock_smf_path = self.options.get( "mock_smf_path", None )
            try:
                if os.getenv( str( self.ip_address ) ) is not None:
                    self.ip_address = os.getenv( str( self.ip_address ) )
                else:
                    main.log.info( self.name + ": ip set to " + self.ip_address )
            except KeyError:
                main.log.info( self.name + ": Invalid host name," +
                              "defaulting to 'localhost' instead" )
                self.ip_address = 'localhost'
            except Exception as e:
                main.log.error( "Uncaught exception: " + str( e ) )

            self.handle = super( MockSMFDriver, self ).connect(
                user_name=self.user_name,
                ip_address=self.ip_address,
                port=None,
                pwd=self.pwd )
            if self.handle:
                main.log.info( "Connection successful to the host " +
                               self.user_name +
                               "@" +
                               self.ip_address )
                self.handle.sendline( "" )
                self.handle.expect( self.prompt )
                return main.TRUE
            else:
                main.log.error( "Connection failed to " +
                                self.user_name +
                                "@" +
                                self.ip_address )
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def startSMF( self, pcap_file="mock_smf.pcap", timeout=10 ):
        """
        Start Mock SMF and connect to the given UPF address.
        """
        #TODO: add interface option?
        try:
            main.log.debug( self.name + ": Starting Mock SMF CLI" )
            # TODO: Add pcap logging folder and other options
            cmd = "pfcpsim &"
            #if pcap_file:
                # TODO: Start pcap separately for go based mock smf
            if self.mock_smf_path:
                self.handle.sendline( "cd " + self.mock_smf_path )
                self.handle.expect( self.prompt )
                main.log.debug( self.handle.before )
            self.handle.sendline( cmd )
            i = self.handle.expect( [ "command not found",
                                      "unknown",
                                      "password for",
                                      self.prompt,
                                      pexpect.TIMEOUT ], timeout )
            #TODO refactor this
            if i == 2:
                main.log.debug( "%s: Sudo asking for password" % self.name )
                self.handle.sendline( self.pwd if self.pwd else "jenkins"  )
                j = self.handle.expect( [ "not found", self.prompt ] )
                if j == 0:
                    main.log.error( "%s: Error starting mock smf" % self.name )
                    main.log.debug( self.handle.before + str( self.handle.after ) )
                    main.cleanAndExit()
            elif i == 3:
                # Exit backgrounded pcfpsim, even if test aborts early
                self.preDisconnect = self.stop
            else:
                main.log.error( "%s: Error starting mock smf" % self.name )
                main.log.debug( self.handle.before + str( self.handle.after ) )
                main.cleanAndExit()
            return main.TRUE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def sendline( self, cmd, timeout=10 ):
        """
        Handles the cli output from the mock smf. Returns main.TRUE if no error, else main.FALSE
        """
        try:
            main.log.debug( "%s: Sending %s" % ( self.name, cmd ) )
            self.handle.sendline( "pfcpctl %s" % cmd )
            i = self.handle.expect( [ "command not found",
                                      "unknown",
                                      "ERRO",
                                      "FATA",
                                      self.prompt,
                                      pexpect.TIMEOUT ], timeout )
            if i == 4:
                return main.TRUE
            else:
                main.log.error( "%s: Error with mock smf cmd: %s" % ( self.name, cmd ) )
                output = self.handle.before + str( self.handle.after )
                if i < 3:
                    # If not timeout, make sure we get rest of prompt from buffer
                    self.handle.expect( [ self.prompt,  pexpect.TIMEOUT ], timeout )
                    output += self.handle.before
                main.log.debug( "%s:%s" % ( self.name, output ) )
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def configure( self, n3_addr, upf_addr, upf_port=None ):
        """
        Configure pfcpsim to connect to upf
        """
        try:
            cmd = "service configure --n3-addr %s --remote-peer-addr %s%s" % (n3_addr,
                    upf_addr,
                    "" if not upf_port else ":%s" % upf_port)
            return self.sendline( cmd )
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def associate( self ):
        """
        Setup PFCP Association
        """
        try:
            cmd = "service associate"
            return self.sendline( cmd )
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def disassociate( self ):
        """
        Teardown PFCP Association
        """
        try:
            cmd = "service disassociate"
            return self.sendline( cmd )
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def create( self, ue_pool, gnb_addr, session_count=1,
                base_id=1, sdf=[] ):
        """
        Create PFCP Session(s)

        Arguements:
            - ue_pool: The IPv4 prefix from which UE addresses will be drawn
            - gnb_addr: The IPv4 address of the eNodeB
        Optional Arguments:
            - session_count: The number of sessions for which UE flows should be
                             created. Defaults to 1
            - base_id: The first id to use for the IDs. Further IDs will be
                       generated by incrementing. Defaults to 1
            - sdf: The sdf filter string to pass to pfcpctl
        """
        try:
            cmd = "session create --count %s --ue-pool %s --gnb-addr %s --baseID %s %s" % (
                  session_count, ue_pool, gnb_addr, base_id,
                  " ".join( sdf ) )
            return self.sendline( cmd )
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def modify( self, ue_pool, gnb_addr, session_count=1,
                base_id=1, buffering=False, notifycp=False ):
        """
        Modify PFCP Sessions(s)

        Arguements:
            - ue_pool: The IPv4 prefix from which UE addresses will be drawn
            - gnb_addr: The IPv4 address of the eNodeB
        Optional Arguments:
            - session_count: The number of sessions for which UE flows should be
                             created. Defaults to 1
            - base_id: The first id to use for the IDs. Further IDs will be
                       generated by incrementing. Defaults to 1
            - buffering: If this argument is present, downlink FARs will have the
                         buffering flag set to true. Defaults to False
            - notifycp: If this argument is present, downlink FARs will have the notify
                        CP flag set to true. Defaults to False
        """
        try:
            cmd = "session modify --count %s --ue-pool %s --gnb-addr %s --baseID %s %s %s" % (
                  session_count, ue_pool, gnb_addr, base_id,
                  "--buffer" if buffering else "",
                  "--notifycp" if notifycp else "" )
            return self.sendline( cmd )
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def delete( self, session_count=1, base_id=1 ):
        """
        Delete PFPC Session(s)

        Arguements:
            - session_count: The number of sessions for which UE flows should be
                             created. Defaults to 1
            - base_id: The first id to use for the IDs. Further IDs will be
                       generated by incrementing. Defaults to 1
        """
        try:
            cmd = "session delete --count %s --baseID %s" % (
                  session_count, base_id )
            return self.sendline( cmd )
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def stop( self ):
        """
        Exits Mock SMF
        """
        try:
            self.handle.sendline( "fg" )
            self.handle.send( "\x03" )
            self.clearBuffer()
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

