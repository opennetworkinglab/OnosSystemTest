#!/usr/bin/env python

"""
Copyright 2021 Open Networking Foundation (ONF)

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

"""

FALSE = '0'
TRUE = '1'
DIR_UPLINK = '1'
DIR_DOWNLINK = '2'
IFACE_ACCESS = '1'
IFACE_CORE = '2'
TUNNEL_SPORT = '2152'
TUNNEL_TYPE_GPDU = '3'


class Up4LibCli():
    """
    Helper library to attach and detach UEs via UP4 P4Runtime APIs.
    """

    @staticmethod
    def attachUe(p4rtCli, s1u_address, enb_address, pfcp_session_id, ue_address,
                 teid=None, up_id=None, down_id=None,
                 teid_up=None, teid_down=None,
                 pdr_id_up=None, far_id_up=None, ctr_id_up=None,
                 pdr_id_down=None, far_id_down=None, ctr_id_down=None,
                 qfi=None, five_g=False):
        Up4LibCli.__programUp4Rules(p4rtCli, s1u_address, enb_address,
                                 pfcp_session_id,
                                 ue_address,
                                 teid, up_id, down_id,
                                 teid_up, teid_down,
                                 pdr_id_up, far_id_up, ctr_id_up,
                                 pdr_id_down, far_id_down, ctr_id_down,
                                 qfi, five_g, action="program")

    @staticmethod
    def detachUe(p4rtCli, s1u_address, enb_address, pfcp_session_id, ue_address,
                 teid=None, up_id=None, down_id=None,
                 teid_up=None, teid_down=None,
                 pdr_id_up=None, far_id_up=None, ctr_id_up=None,
                 pdr_id_down=None, far_id_down=None, ctr_id_down=None,
                 qfi=None, five_g=False):
        Up4LibCli.__programUp4Rules(p4rtCli, s1u_address, enb_address,
                                 pfcp_session_id,
                                 ue_address,
                                 teid, up_id, down_id,
                                 teid_up, teid_down,
                                 pdr_id_up, far_id_up, ctr_id_up,
                                 pdr_id_down, far_id_down, ctr_id_down,
                                 qfi, five_g, action="clear")

    @staticmethod
    def __programUp4Rules(p4rtCli, s1u_address, enb_address, pfcp_session_id,
                          ue_address,
                          teid=None, up_id=None, down_id=None,
                          teid_up=None, teid_down=None,
                          pdr_id_up=None, far_id_up=None, ctr_id_up=None,
                          pdr_id_down=None, far_id_down=None, ctr_id_down=None,
                          qfi=None, five_g=False, action="program"):
        if up_id is not None:
            pdr_id_up = up_id
            far_id_up = up_id
            ctr_id_up = up_id
        if down_id is not None:
            pdr_id_down = down_id
            far_id_down = down_id
            ctr_id_down = down_id
        if teid is not None:
            teid_up = teid
            teid_down = teid

        entries = []

        # ========================#
        # PDR Entries
        # ========================#

        # Uplink
        tableName = 'PreQosPipe.pdrs'
        actionName = ''
        matchFields = {}
        actionParams = {}
        if qfi is None:
            actionName = 'PreQosPipe.set_pdr_attributes'
        else:
            actionName = 'PreQosPipe.set_pdr_attributes_qos'
            if five_g:
                # TODO: currently QFI_MATCH is unsupported in TNA
                matchFields['has_qfi'] = TRUE
                matchFields["qfi"] = str(qfi)
            actionParams['needs_qfi_push'] = FALSE
            actionParams['qfi'] = str(qfi)
        # Match fields
        matchFields['src_iface'] = IFACE_ACCESS
        matchFields['ue_addr'] = str(ue_address)
        matchFields['teid'] = str(teid_up)
        matchFields['tunnel_ipv4_dst'] = str(s1u_address)
        # Action params
        actionParams['id'] = str(pdr_id_up)
        actionParams['fseid'] = str(pfcp_session_id)
        actionParams['ctr_id'] = str(ctr_id_up)
        actionParams['far_id'] = str(far_id_up)
        actionParams['needs_gtpu_decap'] = TRUE
        if not Up4LibCli.__add_entry(p4rtCli, tableName, actionName, matchFields,
                                  actionParams, entries, action):
            return False

        # Downlink
        tableName = 'PreQosPipe.pdrs'
        actionName = ''
        matchFields = {}
        actionParams = {}
        if qfi is None:
            actionName = 'PreQosPipe.set_pdr_attributes'
        else:
            actionName = 'PreQosPipe.set_pdr_attributes_qos'
            # TODO: currently QFI_PUSH is unsupported in TNA
            actionParams['needs_qfi_push'] = TRUE if five_g else FALSE
            actionParams['qfi'] = str(qfi)
        # Match fields
        matchFields['src_iface'] = IFACE_CORE
        matchFields['ue_addr'] = str(ue_address)
        # Action params
        actionParams['id'] = str(pdr_id_down)
        actionParams['fseid'] = str(pfcp_session_id)
        actionParams['ctr_id'] = str(ctr_id_down)
        actionParams['far_id'] = str(far_id_down)
        actionParams['needs_gtpu_decap'] = FALSE
        if not Up4LibCli.__add_entry(p4rtCli, tableName, actionName, matchFields,
                                  actionParams, entries, action):
            return False

        # ========================#
        # FAR Entries
        # ========================#

        # Uplink
        tableName = 'PreQosPipe.load_far_attributes'
        actionName = 'PreQosPipe.load_normal_far_attributes'
        matchFields = {}
        actionParams = {}

        # Match fields
        matchFields['far_id'] = str(far_id_up)
        matchFields['session_id'] = str(pfcp_session_id)
        # Action params
        actionParams['needs_dropping'] = FALSE
        actionParams['notify_cp'] = FALSE
        if not Up4LibCli.__add_entry(p4rtCli, tableName, actionName, matchFields,
                                  actionParams, entries, action):
            return False

        # Downlink
        tableName = 'PreQosPipe.load_far_attributes'
        actionName = 'PreQosPipe.load_tunnel_far_attributes'
        matchFields = {}
        actionParams = {}

        # Match fields
        matchFields['far_id'] = str(far_id_down)
        matchFields['session_id'] = str(pfcp_session_id)
        # Action params
        actionParams['needs_dropping'] = FALSE
        actionParams['notify_cp'] = FALSE
        actionParams['needs_buffering'] = FALSE
        actionParams['tunnel_type'] = TUNNEL_TYPE_GPDU
        actionParams['src_addr'] = str(s1u_address)
        actionParams['dst_addr'] = str(enb_address)
        actionParams['teid'] = str(teid_down)
        actionParams['sport'] = TUNNEL_SPORT
        if not Up4LibCli.__add_entry(p4rtCli, tableName, actionName, matchFields,
                                  actionParams, entries, action):
            return False

        if action == "program":
            main.log.info("All entries added successfully.")
        elif action == "clear":
            Up4LibCli.__clear_entries(p4rtCli, entries)

    @staticmethod
    def __add_entry(p4rtCli, tableName, actionName, matchFields, actionParams,
                    entries, action):
        if action == "program":
            p4rtCli.buildP4RtTableEntry(tableName=tableName,
                                        actionName=actionName,
                                        actionParams=actionParams,
                                        matchFields=matchFields)
            if p4rtCli.pushTableEntry(debug=True) == main.TRUE:
                main.log.info("*** Entry added.")
            else:
                main.log.error("Error during table insertion")
                Up4LibCli.__clear_entries(p4rtCli, entries)
                return False
        entries.append({"tableName": tableName, "actionName": actionName,
                        "matchFields": matchFields,
                        "actionParams": actionParams})
        return True

    @staticmethod
    def __clear_entries(p4rtCli, entries):
        for i, entry in enumerate(entries):
            p4rtCli.buildP4RtTableEntry(**entry)
            if p4rtCli.deleteTableEntry(debug=True) == main.TRUE:
                main.log.info("*** Entry %d of %d deleted." % (i + 1, len(entries)))
            else:
                main.log.error("Error during table delete")
