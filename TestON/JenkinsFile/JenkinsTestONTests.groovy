#!groovy

def getAllTheTests( wikiPrefix ){
    return [
        "FUNC":[
                "FUNCipv6Intent" : [ "basic":true, "extra_A":false, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "FUNCipv6Intent", wiki_file:"FUNCipv6IntentWiki.txt" ],
                "FUNCoptical" :    [ "basic":true, "extra_A":false, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "FUNCoptical", wiki_file:"FUNCopticalWiki.txt" ],
                "FUNCflow" :       [ "basic":true, "extra_A":false, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "FUNCflow", wiki_file:"FUNCflowWiki.txt" ],
                "FUNCnetCfg":      [ "basic":true, "extra_A":false, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "FUNCnetCfg", wiki_file:"FUNCnetCfgWiki.txt" ],
                "FUNCovsdbtest" :  [ "basic":true, "extra_A":false, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "FUNCovsdbtestWiki", wiki_file:"FUNCovsdbtestWiki.txt" ],
                "FUNCnetconf" :    [ "basic":true, "extra_A":false, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "FUNCnetconf", wiki_file:"FUNCnetconfWiki.txt" ],
                "FUNCgroup" :      [ "basic":true, "extra_A":false, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "FUNCgroup", wiki_file:"FUNCgroupWiki.txt" ],
                "FUNCintent" :     [ "basic":false, "extra_A":true, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "FUNCintent", wiki_file:"FUNCintentWiki.txt" ],
                "FUNCintentRest" : [ "basic":false, "extra_A":false, "extra_B":true, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "FUNCintentRest", wiki_file:"FUNCintentRestWiki.txt" ],
                "FUNCformCluster" :[ "basic":true, "extra_A":false, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "FUNCformCluster", wiki_file:"FUNCformClusterWiki.txt" ]
        ],
        "HA":[
                "HAsanity" :                [ "basic":true, "extra_A":false, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "HA Sanity", wiki_file:"HAsanityWiki.txt"  ],
                "HAclusterRestart" :        [ "basic":true, "extra_A":false, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "HA Cluster Restart", wiki_file:"HAclusterRestartWiki.txt"  ],
                "HAsingleInstanceRestart" : [ "basic":true, "extra_A":false, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "HA Single Instance Restart", wiki_file:"HAsingleInstanceRestartWiki.txt"  ],
                "HAstopNodes" :             [ "basic":false, "extra_A":true, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "HA Stop Nodes", wiki_file:"HAstopNodes.txt"  ],
                "HAfullNetPartition" :      [ "basic":false, "extra_A":true, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "HA Full Network Partition", wiki_file:"HAfullNetPartitionWiki.txt"  ],
                "HAswapNodes" :             [ "basic":false, "extra_A":false, "extra_B":true, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "HA Swap Nodes", wiki_file:"HAswapNodesWiki.txt"  ],
                "HAscaling" :               [ "basic":false, "extra_A":false, "extra_B":true, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "HA Scaling", wiki_file:"HAscalingWiki.txt"  ],
                "HAkillNodes" :             [ "basic":false, "extra_A":false, "extra_B":true, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "HA Kill Nodes", wiki_file:"HAkillNodes.txt" ],
                "HAbackupRecover" :         [ "basic":false, "extra_A":false, "extra_B":true, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "HA Backup Recover", wiki_file:"HAbackupRecoverWiki.txt"  ],
                "HAupgrade" :               [ "basic":false, "extra_A":true, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "HA Upgrade", wiki_file:"HAupgradeWiki.txt"  ],
                "HAupgradeRollback" :       [ "basic":false, "extra_A":true, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "HA Upgrade Rollback", wiki_file:"HAupgradeRollbackWiki.txt" ]
        ],
        "SCPF":[
                "SCPFswitchLat":                           [ "basic":true, "extra_A":false, "extra_B":false, "extra_C":false, "extra_D":false, "new_Test":false, day:"" ],
                "SCPFcbench":                              [ "basic":true, "extra_A":false, "extra_B":false, "extra_C":false, "extra_D":false, "new_Test":false, day:"" ],
                "SCPFportLat":                             [ "basic":true, "extra_A":false, "extra_B":false, "extra_C":false, "extra_D":false, "new_Test":false, day:"" ],
                "SCPFflowTp1g":                            [ "basic":true, "extra_A":false, "extra_B":false, "extra_C":false, "extra_D":false, "new_Test":false, day:"" ],
                "SCPFintentEventTp":                       [ "basic":true, "extra_A":false, "extra_B":false, "extra_C":false, "extra_D":false, "new_Test":false, day:"" ],
                "SCPFhostLat":                             [ "basic":false, "extra_A":true, "extra_B":false, "extra_C":false, "extra_D":false, "new_Test":false, day:"" ],
                "SCPFbatchFlowResp":                       [ "basic":false, "extra_A":true, "extra_B":false, "extra_C":false, "extra_D":false, "new_Test":false, day:"" ],
                "SCPFintentRerouteLat":                    [ "basic":false, "extra_A":true, "extra_B":false, "extra_C":false, "extra_D":false, "new_Test":false, day:"" ],
                "SCPFintentInstallWithdrawLat":            [ "basic":false, "extra_A":true, "extra_B":false, "extra_C":false, "extra_D":false, "new_Test":false, day:"" ],
                "SCPFflowTp1gWithFlowObj":                 [ "basic":false, "extra_A":false, "extra_B":true, "extra_C":false, "extra_D":false, "new_Test":false, day:"" ],
                "SCPFintentEventTpWithFlowObj":            [ "basic":false, "extra_A":false, "extra_B":true, "extra_C":false, "extra_D":false, "new_Test":false, day:"" ],
                "SCPFintentRerouteLatWithFlowObj":         [ "basic":false, "extra_A":false, "extra_B":true, "extra_C":false, "extra_D":false, "new_Test":false, day:"" ],
                "SCPFscalingMaxIntentsWithFlowObj":        [ "basic":false, "extra_A":false, "extra_B":true, "extra_C":false, "extra_D":false, "new_Test":false, day:"" ],
                "SCPFintentInstallWithdrawLatWithFlowObj": [ "basic":false, "extra_A":false, "extra_B":true, "extra_C":false, "extra_D":false, "new_Test":false, day:"" ],
                "SCPFscaleTopo":                           [ "basic":false, "extra_A":false, "extra_B":false, "extra_C":true, "extra_D":false, "new_Test":false, day:"" ],
                "SCPFscalingMaxIntents":                   [ "basic":false, "extra_A":false, "extra_B":false, "extra_C":false, "extra_D":true, "new_Test":false, day:"" ],
                "SCPFmastershipFailoverLat":               [ "basic":false, "extra_A":false, "extra_B":false, "extra_C":false, "extra_D":true, "new_Test":false, day:"" ]
        ],
        "USECASE":[
                "FUNCvirNetNB" :                [ "basic":true, "extra_A":false, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "FUNCvirNetNB", wiki_file:"FUNCvirNetNBWiki.txt"  ],
                "FUNCbgpls" :                   [ "basic":true, "extra_A":false, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "FUNCbgpls", wiki_file:"FUNCbgplsWiki.txt"  ],
                "VPLSBasic" :                   [ "basic":true, "extra_A":false, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "VPLSBasic", wiki_file:"VPLSBasicWiki.txt"  ],
                "VPLSfailsafe" :                [ "basic":true, "extra_A":false, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "VPLSfailsafe", wiki_file:"VPLSfailsafeWiki.txt"  ],
                "USECASE_SdnipFunction":        [ "basic":true, "extra_A":false, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "SDNIP Function", wiki_file:"USECASE_SdnipFunctionWiki.txt"  ],
                "USECASE_SdnipFunctionCluster": [ "basic":true, "extra_A":false, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "SDNIP Function Cluster", wiki_file:"USECASE_SdnipFunctionClusterWiki.txt" ],
                "PLATdockertest":               [ "basic":false, "extra_A":true, "extra_B":false, "new_Test":false, "day":"", wiki_link:"Docker Images sanity test", wiki_file:"PLATdockertestTableWiki.txt"  ]
        ],
        "SR":[
                "SRBridging":                   [ "basic":true, "extra_A":false, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "SR Bridging", wiki_file:"SRBridgingWiki.txt" ],
                "SRRouting":                    [ "basic":true, "extra_A":false, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "SR Routing", wiki_file:"SRRoutingWiki.txt" ],
                "SRDhcprelay":                  [ "basic":true, "extra_A":false, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "SR Dhcp Relay", wiki_file:"SRDhcprelayWiki.txt" ],
                "SRDynamicConf":                [ "basic":true, "extra_A":false, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "SR Dynamic Config", wiki_file:"SRDynamicConfWiki.txt" ],
                "SRMulticast":                  [ "basic":true, "extra_A":false, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "SR Multi Cast", wiki_file:"SRMulticastWiki.txt" ],
                "SRSanity":                     [ "basic":false, "extra_A":true, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "SR Sanity", wiki_file:"SRSanityWiki.txt"  ],
                "SRSwitchFailure":              [ "basic":false, "extra_A":true, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "SR Switch Failure", wiki_file:"SRSwitchFailureWiki.txt"  ],
                "SRLinkFailure":                [ "basic":false, "extra_A":true, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "SR Link Failure", wiki_file:"SRLinkFailureWiki.txt"  ],
                "SROnosFailure":                [ "basic":false, "extra_A":true, "extra_B":false, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "SR Onos node Failure", wiki_file:"SROnosFailureWiki.txt"  ],
                "SRClusterRestart":             [ "basic":false, "extra_A":false, "extra_B":true, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "SR Cluster Restart", wiki_file:"SRClusterRestartWiki.txt"  ],
                "SRDynamic":                    [ "basic":false, "extra_A":false, "extra_B":true, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "SR Dynamic", wiki_file:"SRDynamicWiki.txt"  ],
                "SRHighAvailability":           [ "basic":false, "extra_A":false, "extra_B":true, "new_Test":false, "day":"", wiki_link:wikiPrefix + "-" + "SR High Availability", wiki_file:"SRHighAvailabilityWiki.txt"  ]
        ]
    ];
}

return this;
