"""
Copyright 2021 Open Networking Foundation (ONF)

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

"""

import pexpect
import os
from drivers.common.clidriver import CLI


class P4RuntimeCliDriver(CLI):
    """
    Implements a P4Runtime Client CLI-based driver to control devices that uses
    the P4Runtime Protocol, using the P4Runtime shell CLI.

    This driver requires that P4Runtime CLI is configured to not generated colored
    text. To do so, add the following lines to a file in
    ~/.ipython/profile_default/ipython_config.py:
        c.InteractiveShell.color_info = False
        c.InteractiveShell.colors = 'NoColor'
        c.TerminalInteractiveShell.color_info = False
        c.TerminalInteractiveShell.colors = 'NoColor'
    """

    def __init__(self):
        """
        Initialize client
        """
        super(P4RuntimeCliDriver, self).__init__()
        self.name = None
        self.handle = None
        self.p4rtAddress = "localhost"
        self.p4rtPort = "9559"  # Default P4RT server port
        self.prompt = "\$"
        self.p4rtShPrompt = ">>>"
        self.p4rtDeviceId = "1"
        self.p4rtElectionId = "0,100"  # (high,low)
        self.p4rtConfig = None  # Can be used to pass a path to the P4Info and pipeline config

    def connect(self, **connectargs):
        """
        Creates the ssh handle for the P4Runtime CLI
        The ip_address would come from the topo file using the host tag, the
        value can be an environment variable as well as a "localhost" to get
        the ip address needed to ssh to the "bench"
        """
        try:
            for key in connectargs:
                vars(self)[key] = connectargs[key]
            self.name = self.options.get("name", "")
            self.p4rtAddress = self.options.get("p4rt_address", "localhost")
            self.p4rtPort = self.options.get("p4rt_port", "9559")
            self.p4rtShPrompt = self.options.get("p4rt_sh_prompt", ">>>")
            self.p4rtDeviceId = self.options.get("p4rt_device_id", "1")
            self.p4rtElectionId = self.options.get("p4rt_election_id", "0,100")
            self.p4rtConfig = self.options.get("p4rt_config", None)
            try:
                if os.getenv(str(self.ip_address)) is not None:
                    self.ip_address = os.getenv(str(self.ip_address))
                else:
                    main.log.info(self.name + ": ip set to " + self.ip_address)
            except KeyError:
                main.log.info(self.name + ": Invalid host name," +
                              "defaulting to 'localhost' instead")
                self.ip_address = 'localhost'
            except Exception as inst:
                main.log.error("Uncaught exception: " + str(inst))

            self.handle = super(P4RuntimeCliDriver, self).connect(
                user_name=self.user_name,
                ip_address=self.ip_address,
                port=None,
                pwd=self.pwd)
            if self.handle:
                main.log.info("Connection successful to the host " +
                              self.user_name +
                              "@" +
                              self.ip_address)
                self.handle.sendline("")
                self.handle.expect(self.prompt)
                return main.TRUE
            else:
                main.log.error("Connection failed to " +
                               self.user_name +
                               "@" +
                               self.ip_address)
                return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanAndExit()
        except Exception:
            main.log.exception(self.name + ": Uncaught exception!")
            main.cleanAndExit()

    def startP4RtClient(self, pushConfig=False):
        """
        Start the P4Runtime shell CLI client

        :param pushConfig: True if you want to push the pipeline config, False otherwise
            requires the p4rt_config configuration parameter to be set
        :return:
        """
        try:
            main.log.debug(self.name + ": Starting P4Runtime Shell CLI")
            grpcAddr = "%s:%s" % (self.p4rtAddress, self.p4rtPort)
            startP4RtShLine = "python3 -m p4runtime_sh --grpc-addr " + grpcAddr + \
                              " --device-id " + self.p4rtDeviceId + \
                              " --election-id " + self.p4rtElectionId
            if pushConfig:
                if self.p4rtConfig:
                    startP4RtShLine += " --config " + self.p4rtConfig
                else:
                    main.log.error(
                        "You should provide a P4 Runtime config to push!")
                    main.cleanAndExit()
            response = self.__clearSendAndExpect(startP4RtShLine)
            self.preDisconnect = self.stopP4RtClient
        except pexpect.TIMEOUT:
            main.log.exception(self.name + ": Command timed out")
            return main.FALSE
        except pexpect.EOF:
            main.log.exception(self.name + ": connection closed.")
            main.cleanAndExit()
        except Exception:
            main.log.exception(self.name + ": Uncaught exception!")
            main.cleanAndExit()

    def stopP4RtClient(self):
        """
        Exit the P4Runtime shell CLI
        """
        try:
            main.log.debug(self.name + ": Stopping P4Runtime Shell CLI")
            self.handle.sendline("exit")
            self.handle.expect(self.prompt)
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception(self.name + ": Command timed out")
            return main.FALSE
        except pexpect.EOF:
            main.log.exception(self.name + ": connection closed.")
            main.cleanAndExit()
        except Exception:
            main.log.exception(self.name + ": Uncaught exception!")
            main.cleanAndExit()

    def pushTableEntry(self, tableEntry=None, debug=True):
        """
        Push a table entry with either the given table entry or use the saved
        table entry in the variable 'te'.

        Example of a valid tableEntry string:
        te = table_entry["FabricIngress.forwarding.routing_v4"](action="set_next_id_routing_v4"); te.action["next_id"] = "10"; te.match["ipv4_dst"] = "10.0.0.0" # nopep8

        :param tableEntry: the string table entry, if None it uses the table
            entry saved in the 'te' variable
        :param debug: True to enable debug logging, False otherwise
        :return: main.TRUE or main.FALSE on error
        """
        try:
            main.log.debug(self.name + ": Pushing Table Entry")
            if debug:
                self.handle.sendline("te")
                self.handle.expect(self.p4rtShPrompt)
            pushCmd = ""
            if tableEntry:
                pushCmd = tableEntry + ";"
            pushCmd += "te.insert()"
            response = self.__clearSendAndExpect(pushCmd)
            if "Traceback" in response or "Error" in response:
                # TODO: other possibile errors?
                # NameError...
                main.log.error(
                    self.name + ": Error in pushing table entry: " + response)
                return main.FALSE
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception(self.name + ": Command timed out")
            return main.FALSE
        except pexpect.EOF:
            main.log.exception(self.name + ": connection closed.")
            main.cleanAndExit()
        except Exception:
            main.log.exception(self.name + ": Uncaught exception!")
            main.cleanAndExit()

    def deleteTableEntry(self, tableEntry=None, debug=True):
        """
        Deletes a table entry with either the given table entry or use the saved
        table entry in the variable 'te'.

        Example of a valid tableEntry string:
        te = table_entry["FabricIngress.forwarding.routing_v4"](action="set_next_id_routing_v4"); te.action["next_id"] = "10"; te.match["ipv4_dst"] = "10.0.0.0" # nopep8

        :param tableEntry: the string table entry, if None it uses the table
            entry saved in the 'te' variable
        :param debug: True to enable debug logging, False otherwise
        :return: main.TRUE or main.FALSE on error
        """
        try:
            main.log.debug(self.name + ": Deleting Table Entry")
            if debug:
                self.__clearSendAndExpect("te")
            pushCmd = ""
            if tableEntry:
                pushCmd = tableEntry + ";"
            pushCmd += "te.delete()"
            response = self.__clearSendAndExpect(pushCmd)
            main.log.debug(
                self.name + ": Delete table entry response: {}".format(
                    response))
            if "Traceback" in response or "Error" in response:
                # TODO: other possibile errors?
                # NameError...
                main.log.error(
                    self.name + ": Error in deleting table entry: " + response)
                return main.FALSE
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception(self.name + ": Command timed out")
            return main.FALSE
        except pexpect.EOF:
            main.log.exception(self.name + ": connection closed.")
            main.cleanAndExit()
        except Exception:
            main.log.exception(self.name + ": Uncaught exception!")
            main.cleanAndExit()

    def buildP4RtTableEntry(self, tableName, actionName, actionParams={},
                            matchFields={}):
        """
        Build a Table Entry
        :param tableName: The name of table
        :param actionName: The name of the action
        :param actionParams: A dictionary containing name and values for the action parameters
        :param matchFields: A dictionary containing name and values for the match fields
        :return: main.TRUE or main.FALSE on error
        """
        # TODO: improve error checking when creating the table entry, add
        #  params, and match fields.
        try:
            main.log.debug(self.name + ": Building P4RT Table Entry")
            cmd = 'te = table_entry["%s"](action="%s"); ' % (
                tableName, actionName)

            # Action Parameters
            for name, value in actionParams.items():
                cmd += 'te.action["%s"]="%s";' % (name, str(value))

            # Match Fields
            for name, value in matchFields.items():
                cmd += 'te.match["%s"]="%s";' % (name, str(value))

            response = self.__clearSendAndExpect(cmd)
            if "Unknown action" in response:
                main.log.error("Unknown action: " + response)
                return main.FALSE
            if "AttributeError" in response:
                main.log.error("Wrong action: " + response)
                return main.FALSE
            if "Invalid value" in response:
                main.log.error("Invalid action value: " + response)
                return main.FALSE
            if "Action parameter value must be a string" in response:
                main.log.error(
                    "Action parameter value must be a string: " + response)
                return main.FALSE
            if "table" in response and "does not exist" in response:
                main.log.error("Unknown table: " + response)
                return main.FALSE
            if "not a valid match field name" in response:
                main.log.error("Invalid match field name: " + response)
                return main.FALSE
            if "is not a valid" in response:
                main.log.error("Invalid match field: " + response)
                return main.FALSE
            if "Traceback" in response:
                main.log.error("Error in creating the table entry: " + response)
                return main.FALSE
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception(self.name + ": Command timed out")
            return main.FALSE
        except pexpect.EOF:
            main.log.exception(self.name + ": connection closed.")
            main.cleanAndExit()
        except Exception:
            main.log.exception(self.name + ": Uncaught exception!")
            main.cleanAndExit()

    def disconnect(self):
        """
        Called at the end of the test to stop the p4rt CLI component and
        disconnect the handle.
        """
        response = main.TRUE
        try:
            if self.handle:
                self.handle.sendline("")
                i = self.handle.expect([self.p4rtShPrompt, pexpect.TIMEOUT],
                                       timeout=2)
                if i != 1:
                    # If the p4rtShell is still connected make sure to
                    # disconnect it before
                    self.stopP4RtClient()
                i = self.handle.expect([self.prompt, pexpect.TIMEOUT],
                                       timeout=2)
                if i == 1:
                    main.log.warn(
                        self.name + ": timeout when waiting for response")
                    main.log.warn(
                        self.name + ": response: " + str(self.handle.before))
                self.handle.sendline("exit")
                i = self.handle.expect(["closed", pexpect.TIMEOUT], timeout=2)
                if i == 1:
                    main.log.warn(
                        self.name + ": timeout when waiting for response")
                    main.log.warn(
                        self.name + ": response: " + str(self.handle.before))
            return main.TRUE
        except TypeError:
            main.log.exception(self.name + ": Object not as expected")
            response = main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
        except ValueError:
            main.log.exception("Exception in disconnect of " + self.name)
            response = main.TRUE
        except Exception:
            main.log.exception(self.name + ": Connection failed to the host")
            response = main.FALSE
        return response

    def __clearSendAndExpect(self, cmd):
        self.clearBuffer()
        self.handle.sendline(cmd)
        self.handle.expect(self.p4rtShPrompt)
        return self.handle.before

    def clearBuffer(self, debug=False):
        """
        Keep reading from buffer until it's empty
        """
        i = 0
        response = ''
        while True:
            try:
                i += 1
                # clear buffer
                if debug:
                    main.log.warn("%s expect loop iteration" % i)
                self.handle.expect(self.p4rtShPrompt, timeout=5)
                response += self.cleanOutput(self.handle.before, debug)
            except pexpect.TIMEOUT:
                return response
