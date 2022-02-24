from tests.USECASE.SegmentRouting.dependencies.Testcaselib import \
    Testcaselib as run
from tests.USECASE.SegmentRouting.dependencies.trex import Trex
import json


class QOSNonMobileTest:

    def runTest(self, main, test_idx, n_switches):
        run.initTest(main)
        main.log.info(main.Cluster.numCtrls)
        main.Cluster.setRunningNode(3)
        run.installOnos(main, skipPackage=True, cliSleep=5)

        # Use the first available ONOS instance CLI
        onos_rest = main.Cluster.active(0).REST
        onos_cli = main.Cluster.active(0).CLI

        trex = Trex()
        trex.setup(main.TRexClient)
        try:
            # Load traffic config for the current test case
            cfgFile = "%s/tests/CASE_%d.json" % (main.configPath, test_idx)
            with open(cfgFile) as cfg:
                testCfg = json.load(cfg)

            original_flows_number = onos_cli.checkFlowCount()

            main.step("Verify slices and traffic Classes")
            slices_onos = onos_rest.getSlices(debug=True)

            # Sanity check for the API, at least the default slice should be there.
            utilities.assert_equal(
                expect=True,
                actual={"SliceId": 0} in json.loads(slices_onos),
                onpass="Default slice verified in slicing service",
                onfail="Error in verifying default slice in slicing service"
            )

            for slice_name in main.params["SLICING"]["slices"]:
                slice = main.params["SLICING"]["slices"][slice_name]
                if "slice_id" not in slice:
                    continue
                slice_id = int(slice["slice_id"])
                utilities.assert_equal(
                    expect=True,
                    actual={"SliceId": slice_id} in json.loads(slices_onos),
                    onpass="Verified presence of slice %s in slicing service" % slice_id,
                    onfail="Slice %s not found in slicing service" % slice_id
                )

                tcs = slice.get("traffic_classes", "").split(",")

                tcs_onos = onos_rest.getTrafficClasses(slice_id=slice_id,
                                                       debug=True)
                for tc in tcs:
                    utilities.assert_equal(
                        expect=True,
                        actual={"TrafficClass": tc} in json.loads(tcs_onos),
                        onpass="Verified presence of TC %s for slice %s in slicing service" % (tc, slice_id),
                        onfail="TC %s not found for slice %s in slicing service" % (tc, slice_id)
                    )

            main.step("Add and verify traffic classifier flows")
            new_flows = 0
            for flow_name in main.params["SLICING"]["traffic_classification"]:
                new_flows += 1
                flow_config = main.params["SLICING"]["traffic_classification"][
                    flow_name]

                traffic_selector = self.__normalizeTrafficSelector(flow_config.get("traffic_selector"))
                onos_rest.addSlicingClassifierFlow(
                    slice_id=int(flow_config.get("slice_id")),
                    traffic_class=flow_config.get("traffic_class"),
                    traffic_selector=traffic_selector,
                    debug=True
                )

                actual_selectors = json.loads(onos_rest.getSlicingClassifierFlows(
                    slice_id=int(flow_config.get("slice_id")),
                    traffic_class=flow_config.get("traffic_class"),
                    debug=True
                ))
                utilities.assert_equal(
                    expect=True,
                    actual=self.__containsTrafficSelector(actual_selectors, traffic_selector),
                    onpass="Classifier flow %s installed" % flow_name,
                    onfail="Classifier flow %s not found after insert" % flow_name
                )

            run.checkFlows(
                main,
                minFlowCount=original_flows_number + (new_flows * n_switches)
            )

            for flow in testCfg["flows"]:
                trex.createFlow(flow)
            results = trex.sendAndReceiveTraffic(testCfg["duration"])
            main.step("Verify congestion")
            trex.verifyCongestion(results)

            trex.logPortStats()
            for flow in testCfg["flows"]:
                trex.logFlowStats(flow)

            # Assert Flow Stats
            for flow in testCfg["flows"]:
                if trex.isFlowStats(flow):
                    main.step("{}: Assert RX Packets".format(flow))
                    trex.assertRxPackets(flow)
                    main.step("{}: Assert Dropped Packets".format(flow))
                    trex.assertDroppedPacket(flow)
                    main.step("{}: Assert 99.9 Percentile Latency".format(flow))
                    trex.assert99_9PercentileLatency(flow)

            main.step("Remove and verify traffic classifier flows")
            for flow_name in main.params["SLICING"]["traffic_classification"]:
                flow_config = main.params["SLICING"]["traffic_classification"][
                    flow_name]

                traffic_selector = self.__normalizeTrafficSelector(flow_config.get("traffic_selector"))
                onos_rest.removeSlicingClassifierFlow(
                    slice_id=int(flow_config.get("slice_id")),
                    traffic_class=flow_config.get("traffic_class"),
                    traffic_selector=traffic_selector,
                    debug=True
                )
                actual_selectors = json.loads(onos_rest.getSlicingClassifierFlows(
                    slice_id=int(flow_config.get("slice_id")),
                    traffic_class=flow_config.get("traffic_class"),
                    debug=True
                ))
                utilities.assert_equal(
                    expect=False,
                    actual=self.__containsTrafficSelector(actual_selectors, traffic_selector),
                    onpass="Classifier flow %s removed from slicing service" % flow_name,
                    onfail="Unable to remove classifier flow %s from slicing service" % flow_name
                )

            run.checkFlows(main, minFlowCount=original_flows_number)
        finally:
            main.step("Teardown")
            trex.teardown()
            run.cleanup(main)

    def __normalizeTrafficSelector(self, traffic_selector):
        ts = {
            "criteria": [traffic_selector[criterion] for criterion in
                         traffic_selector]}
        # Converts the required fields into integer, required to compare them
        # with the API result from ONOS.
        for criterion in ts["criteria"]:
            if "udpPort" in criterion:
                criterion["udpPort"] = int(criterion["udpPort"])
            elif "protocol" in criterion:
                criterion["protocol"] = int(criterion["protocol"])
        return ts

    def __containsTrafficSelector(self, actual_selectors, expected_selector):
        # actual_selectors = [{"criteria":[{"type":"IP_PROTO","protocol":17},{"type":"UDP_DST","udpPort":200}]}]
        expected_criteria = expected_selector["criteria"]
        for actual_selector in actual_selectors:
            actual_criteria = actual_selector["criteria"]
            if len(actual_criteria) != len(expected_criteria):
                continue
            for actual_criterion in actual_criteria:
                # actual_criterion = {"type":"IP_PROTO","protocol":17}
                if actual_criterion not in expected_criteria:
                    # Next selector
                    break
            else:
                # We found all criteria in this selector.
                return True
        return False
