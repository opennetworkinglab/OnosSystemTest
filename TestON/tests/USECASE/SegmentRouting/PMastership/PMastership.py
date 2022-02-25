class PMastership:

    def __init__(self):
        self.default = ''

    def CASE1(self, main):
        main.case("PMastership Test")
        """
        Verify there are no pending flows and groups
        Get flows and group counts
        Verify that are not 0
        Get the master of leaf2 (look at the params file for the config)
        Verify that has the master
        Kill switch leaf2
        Set label on switch K8S node to prevent K8S to redeploy stratum
        Verify there are no pending flows and groups related to segment routing
        Verify that the master of leaf2 is still the same as before
        Wait for the switch to be up again
        Verify there are no pending flows and groups
        """
        try:
            from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
                Testcaselib as run
            from tests.USECASE.SegmentRouting.SRStaging.dependencies.SRStagingTest import \
                SRStagingTest
            import time
        except ImportError as e:
            main.log.error("Import not found. Exiting the test")
            main.log.error(e)
            main.cleanAndExit()
        # Retrieves the params of the test
        n_switches = int(main.params["TOPO"]["switchNum"])
        switch_to_kill = main.params["PMastership"]["PMastership_dataplane_fail"]["switch_to_kill"]
        k8s_switch_node = main.params["PMastership"]["PMastership_dataplane_fail"]["k8s_switch_node"]
        k8s_label = main.params["PMastership"]["PMastership_dataplane_fail"]["k8s_label"]
        k8s_label_value_test = main.params["PMastership"]["PMastership_dataplane_fail"]["k8s_label_value_test"]
        k8s_label_value_normal = main.params["PMastership"]["PMastership_dataplane_fail"]["k8s_label_value_normal"]
        # Init the main components and variables
        run.initTest(main)
        main.log.info(main.Cluster.numCtrls)
        main.Cluster.setRunningNode(3)
        run.installOnos(main, skipPackage=True, cliSleep=5)
        onos_cli = main.Cluster.active(0).CLI
        kubectl = main.Cluster.active(0).Bench
        kubeconfig = main.Cluster.active(0).k8s.kubeConfig
        namespace = main.params['kubernetes']['namespace']

        main.step("Verify there are added flows")
        initial_flows_count = onos_cli.checkFlowCount()
        empty = main.TRUE if ( initial_flows_count == 0 ) else main.FALSE
        utilities.assert_equal(
            expect=main.FALSE,
            actual=empty,
            onpass="There are " + str(initial_flows_count) + " added flows",
            onfail="There are no added flows",
        )

        main.step("Verify there are added groups")
        initial_groups_count = onos_cli.checkGroupCount()
        empty = main.TRUE if ( initial_groups_count == 0 ) else main.FALSE
        utilities.assert_equal(
            expect=main.FALSE,
            actual=empty,
            onpass="There are " + str(initial_groups_count) + " added groups",
            onfail="There are no added groups",
        )

        no_pending_flows = utilities.retry(onos_cli.checkFlowsState,
                                           [False, None],
                                           kwargs={"isPENDING": False},
                                           attempts=20,
                                           getRetryingTime=True)

        main.step("Verify there are no pending flows")
        utilities.assert_equal(
            expect=main.TRUE,
            actual=no_pending_flows,
            onpass="There are no pending flows",
            onfail="There are pending flows",
        )

        no_pending_groups = utilities.retry(onos_cli.checkGroupsState,
                                            [False, None],
                                            kwargs={"isPENDING": False},
                                            attempts=20,
                                            getRetryingTime=True)

        main.step("Verify there are no pending groups")
        utilities.assert_equal(
            expect=main.TRUE,
            actual=no_pending_groups,
            onpass="There are no pending groups",
            onfail="There are pending groups",
        )

        main.step("Retrieving " + switch_to_kill + " master")
        initial_master = onos_cli.getMaster("device:" + k8s_switch_node)
        no_master = main.TRUE if ( initial_master is None ) else main.FALSE
        utilities.assert_equal(
            expect=main.FALSE,
            actual=no_master,
            onpass=initial_master + " is the master of " + switch_to_kill,
            onfail="There is no master for " + switch_to_kill,
        )

        main.step("Set label to switch k8s node and kill Stratum")
        # K8s node name correspond to the switch name in lowercase
        utilities.assert_equal(
            expect=main.TRUE,
            actual=kubectl.kubectlSetLabel(
                nodeName=k8s_switch_node,
                label=k8s_label,
                value=k8s_label_value_test,
                kubeconfig=kubeconfig,
                namespace=namespace,
            ),
            onpass="Label has been set correctly on node %s" % k8s_switch_node,
            onfail="Label has not been set on node %s" % k8s_switch_node
        )

        try:
            def checkNumberStratumPods(n_value):
                pods = kubectl.kubectlGetPodNames(
                    kubeconfig=kubeconfig,
                    namespace=namespace,
                    name="stratum"
                )
                main.log.info("PODS: " + str(pods))
                return n_value == len(pods) if pods is not main.FALSE else False
            # Execute the following in try/except/finally to be sure to restore the
            # k8s label even in case of unhandled exception.

            # Wait for stratum pod to be removed from the switch
            removed = utilities.retry(checkNumberStratumPods,
                                      False,
                                      args=[n_switches - 1],
                                      attempts=50)
            main.log.info("Stratum has been removed from the switch? %s" % removed)

            sleepTime = 20
            switch_component = getattr(main, switch_to_kill)
            main.log.info("Sleeping %s seconds for ONOS to react" % sleepTime)
            time.sleep(sleepTime)

            available = utilities.retry(SRStagingTest.switchIsConnected,
                                        True,
                                        args=[switch_component],
                                        attempts=300,
                                        getRetryingTime=True)
            main.log.info("Switch %s is available in ONOS? %s" % (
                switch_to_kill, available))
            utilities.assert_equal(
                expect=True,
                actual=not available and removed,
                onpass="Stratum was removed from switch k8s node",
                onfail="Stratum was not removed from switch k8s node"
            )

            main.step("Verify there are no segmentrouting flows after the failure")
            raw_flows = onos_cli.flows(device="device:" + k8s_switch_node)
            sr_flows = main.TRUE if "segmentrouting" in raw_flows else main.FALSE
            utilities.assert_equal(
                expect=main.FALSE,
                actual=sr_flows,
                onpass="There are no segmentrouting flows",
                onfail="There are segmentrouting flows",
            )

            main.step("Verify there are no segmentrouting groups after the failure")
            raw_groups = onos_cli.groups(device="device:" + k8s_switch_node)
            sr_groups = main.TRUE if "segmentrouting" in raw_groups else main.FALSE
            utilities.assert_equal(
                expect=main.FALSE,
                actual=sr_groups,
                onpass="There are no segmentrouting groups",
                onfail="There are segmentrouting groups",
            )

            main.step("Verify " + initial_master + " is still the master of " + switch_to_kill)
            after_master = onos_cli.getMaster("device:" + k8s_switch_node)
            no_master = main.TRUE if ( initial_master is None ) else main.FALSE
            utilities.assert_equal(
                expect=main.FALSE,
                actual=no_master,
                onpass=initial_master + " is the master of " + switch_to_kill,
                onfail="There is no master for " + switch_to_kill,
            )

            same_master = main.TRUE if ( initial_master == after_master ) else main.FALSE
            utilities.assert_equal(
                expect=main.TRUE,
                actual=same_master,
                onpass=initial_master + " is still the master of " + switch_to_kill,
                onfail="Master for " + switch_to_kill + " is " + after_master,
            )

        except Exception as e:
            main.log.error("Unhandled exception!")
            main.log.error(e)
        finally:
            utilities.assert_equal(
                expect=main.TRUE,
                actual=kubectl.kubectlSetLabel(
                    nodeName=k8s_switch_node,
                    label=k8s_label,
                    value=k8s_label_value_normal,
                    kubeconfig=kubeconfig,
                    namespace=namespace,
                ),
                onpass="Label has been set correctly on node %s" % k8s_switch_node,
                onfail="Label has not been set on node %s" % k8s_switch_node
            )

            # Wait for stratum pod to be re-deployed on the switch
            deployed = utilities.retry(checkNumberStratumPods,
                                       False,
                                       args=[n_switches],
                                       attempts=50)
            main.log.info("Stratum has been redeployed on the switch? %s" % deployed)

            # Wait switch to be back in ONOS
            available = utilities.retry(SRStagingTest.switchIsConnected,
                                        False,
                                        args=[switch_component],
                                        sleep=2,
                                        attempts=300,
                                        getRetryingTime=True)
            main.log.info("Switch %s is available in ONOS? %s" % (
                switch_to_kill, available))
            utilities.assert_equal(
                expect=True,
                actual=available and deployed,
                onpass="Switch is back available in ONOS and stratum has been redeployed",
                onfail="Switch is not available in ONOS, may influence subsequent tests!"
            )

        sleepTime = 10
        main.log.info("Sleeping %s seconds for ONOS to react and assure flows/groups are ADDED" % sleepTime)
        time.sleep(sleepTime)

        main.step("Verify there are added flows after reboot")
        after_flows_count = onos_cli.checkFlowCount()
        empty = main.TRUE if ( after_flows_count == 0 ) else main.FALSE
        utilities.assert_equal(
            expect=main.FALSE,
            actual=empty,
            onpass="There are " + str(after_flows_count) + " added flows",
            onfail="There are no added flows",
        )

        main.step("Verify there are added groups after reboot")
        after_groups_count = onos_cli.checkGroupCount()
        empty = main.TRUE if ( after_groups_count == 0 ) else main.FALSE
        utilities.assert_equal(
            expect=main.FALSE,
            actual=empty,
            onpass="There are " + str(after_groups_count) + " added groups",
            onfail="There are no added groups",
        )

        no_pending_flows = utilities.retry(onos_cli.checkFlowsState,
                                           [False, None],
                                           kwargs={"isPENDING": False},
                                           attempts=20,
                                           getRetryingTime=True)

        main.step("Verify there are no pending flows after reboot")
        utilities.assert_equal(
            expect=main.TRUE,
            actual=no_pending_flows,
            onpass="There are no pending flows",
            onfail="There are pending flows",
        )

        no_pending_groups = utilities.retry(onos_cli.checkGroupsState,
                                            [False, None],
                                            kwargs={"isPENDING": False},
                                            attempts=20,
                                            getRetryingTime=True)

        main.step("Verify there are no pending groups after reboot")
        utilities.assert_equal(
            expect=main.TRUE,
            actual=no_pending_groups,
            onpass="There are no pending groups",
            onfail="There are pending groups",
        )
