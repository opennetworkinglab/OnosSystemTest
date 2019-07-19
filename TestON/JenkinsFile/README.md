# TestON Jenkins Scripts

## General Information

For those unfamiliar with the ONOS QA Jenkins structure, please refer to the [QA Jenkins Structure](https://wiki.onosproject.org/display/ONOS/QA+Jenkins+Structure) page on the ONOS wiki.

ONOS QA Jenkins may be found here: [https://jenkins.onosproject.org/view/QA/](https://jenkins.onosproject.org/view/QA/).

The files in this directory are read from the ONOS [ci-management](https://gerrit.onosproject.org/#/q/project:ci-management) repo and run as pipeline scripts.

## Quick Start

If you are here to add/modify a branch, schedule, or test, you only need to modify the `.json` files in the `dependencies/` directory. Please follow the formatting carefully!

### Adding a Branch
The list of branches is located in `dependencies/branches.json`. The file is constructed in the following format:

- `"latest_branches"` - `dict` of the latest branches for each major ONOS version.
    - `"onos-1.x"` - Latest version of ONOS 1.x (ie: "1.15").
    - `...`
- `"support_branches"` - `dict` of other ONOS support branches that are not necessarily the latest branches.
    - `"onos-1.sb1"` - Support branch 1 of ONOS 1.x (ie: "1.12").
    - `...`

Note: Please avoid adding the `onos-` prefix as the value.
- Correct: `"onos-1.x": 1.15,`
- Incorrect: ~~`"onos-1.x": onos-1.15,`~~

### Adding a Schedule

The list of schedules is located in `dependencies/schedule.json`. The file is constructed in the following format:

- `<schedule name>` - List of abbreviated (first 3 letters) days for the schedule (ie: `["mon", "wed", "fri"]`).

### Adding a Test
The list of tests is located in `dependencies/tests.json`. The file is constructed in the following format:

- `<test name>` - Name of the TestON test.
    - `"wikiName"` - Name of the TestON test as it would appear on the ONOS wiki (this is usually identical to the `<test name>`).
    - `"wikiFile"` - Filename of the text file that the ONOS wiki uses to display the test result summary.
    - `"schedules"` - List of `dict` containing the following:
        - `"branch"` - ONOS branch label mapping from `branches.json`. (ie: "onos-1.x")
        - `"day"` - Name of the schedule from `schedule.json` that this test runs on the given `"branch"` and `"nodeLabel"`. (ie: "weekdays")
        - `"nodeLabel"` - Node label mapping from Jenkins specifying the node to run the test on (ie: "BM").
    - `"category"` - Category of the test (ie: "FUNC").
    - `"supportedBranches"` - List of supported branches the test can run on.

# Scripts

### [Master-Trigger](https://jenkins.onosproject.org/view/QA/job/master-trigger/)

`MasterTrigger.groovy` is the script that runs the `master-trigger` job in ONOS QA Jenkins.  The structure of the script is as follows:

1. Initialization
    - Initializing repo paths in `dependencies/JenkinsPathAndFiles.groovy`.
    - Initializing tests, branches, and schedules lists in `dependencies/JenkinsTestONTests.groovy`.
    - Reading parameters from Jenkins:
        - `manual_run` - If this option is checked, the branches and tests to run will be determined by the parameters from Jenkins. If unchecked, this will be treated as a nightly run; the branches and tests to run are determined in `branches.json` and `tests.json`.
        - `TimeOut` - Time (in minutes) until the entire pipeline is aborted. By default, this is set to 1410 minutes (23 hours 30 minutes). This value is also passed to the downstream jobs.
        - `PostResult` - If `manual_run` is true, the results of the test will be recorded and posted to the ONOS wiki if this option is checked. Otherwise, results of the manually run test will not be recorded.
        - `branches` - If `manual_run` is true, this parameter determines the branches to run as a `\n`-separated list.
        - `Tests` - If `manual_run` is true, this parameter determines the tests to run as a `\n`-separated list.
        - `simulate_day` - If `manual_run` is false, this parameter overrides the day of a nightly test to run (ie: "mon", "wed", etc.) if this option is checked. Otherwise, the current day will be used.
    - Initializing the current date, if triggered by time as a nightly test. If the `simulate_day` parameter is not empty, this overrides the date.
    - Determine branches to run based on the parameters or date if manual or nightly run, respectively.
    - Determine tests to select from the list of tests based on the parameters or date if manual or nightly run, respectively.
    - Initializing graph paths.

2. Run Tests
    - Get valid schedules from `schedules.json` based on the given date. This is ignored in a manual run.
    - Get tests by ONOS branch, node label, and test category, and determine if a test should run if it is set to run on that day (if a test contains a valid schedule based on the given date). Manual runs override this and will always run the provided tests.
    - Create lists of tests from `dependencies/TriggerFuncs.groovy` that run in parallel based on the branch, node label, and test category.
    - Prints list of tests to run.
    - Runs environment setups in parallel and triggers downstream jobs (ie: [FUNC-pipeline-master](https://jenkins.onosproject.org/view/QA/job/FUNC-pipeline-master/)) for each test list.

3. Generate Graphs
    - After all downstream jobs have concluded, [overall graphs](https://wiki.onosproject.org/display/ONOS/ONOS-Master) are generated for each branch and posted to the ONOS wiki.

### [CommonJenkinsFile](https://jenkins.onosproject.org/view/QA/job/FUNC-pipeline-master/)

`CommonJenkinsFile.groovy` handles running TestON tests in sequence, uploading test results to the database, creating plots, and posting the results to the ONOS wiki. This can also be run to manually refresh the wiki graphs. The structure of the script is as follows:

1. Initialization
    - Initializing repo paths in `dependencies/JenkinsPathAndFiles.groovy`.
    - Initializing tests, branches, and schedules lists in `dependencies/JenkinsTestONTests.groovy`.
    - Reading parameters from Jenkins.
        - `OnlyRefreshGraphs` - If this option is checked, the run will only refresh the graphs without running any of the tests.
        - `TimeOut` - Time (in minutes) until the entire pipeline is aborted. By default, this is set to 1410 minutes (23 hours 30 minutes). In a nightly run, the value from the upstream `master-trigger` job is used.
        - `TestStation` - Test station to run the job on.
        - `NodeLabel` - Node label of the test station that runs the job.
        - `TestsOverride` - List of tests to run. Overrides the list in the `.property` file.
        - `Category` - Category of the pipeline. Primarily used when triggered by the upstream `master-trigger` job.
        - `Branch` - Branch of the pipeline. Primarily used when triggered by the upstream `master-trigger` job.
    - Initialize graph related variables and functions.
    - Get test and branch properties from the `.property` file generated by the upstream `master-trigger` job.
    - Initialize graph paths.
    - Generate string list of tests to run, which retrieves a `dict` of tests to run.

2. Run Tests
    - Each test has the environment initialized before running the test. `stc shutdown`, `stc teardown`, and `./cleanup.sh -f` is run before `./cli.py [...]` to ensure another test is not running simultaneously on the same node.
    - Results are recorded and saved onto the database.
    - Logs are exported and summary of results is posted to the ONOS wiki.

3. Generate Graphs
    - Trend graphs (for non-SCPF tests) or test graphs (for SCPF tests) are generated and published to the ONOS wiki.

4. Send to Slack
    - If there was a problem with the test, a message is sent on the ONOS Slack on the channel `#jenkins-related`.
    - The pipeline step result is `failed` if there was at least one problem with the test, and `passed` if there were no problems.

5. Generate Overall Graph
    - Once all tests have concluded, the test category overall graph is generated and published to the ONOS wiki.

### [generateReleaseTestONWiki](https://jenkins.onosproject.org/view/QA/job/generate_wiki_pages/)

`generateReleaseTestONWiki.groovy` generates all necessary test result wiki pages when there is a new version of ONOS about to release. The job needs to be run multiple times in this specific order to generate all pages correctly.
1. First, run the job with the following parameters to generate only the **top-level result page** for that version:
    - `top_level_page_id`: -1
    - `SCPF_page_id`: -1
    - `USECASE_page_id`: -1
2. Second, get the pageID of the top-level result page just generated, and run this job again with `top_level_page_id` as the known pageID to generate the **test category front pages**.
    - `top_level_page_id`: *page ID of top-level result page*
    - `SCPF_page_id`: -1
    - `USECASE_page_id`: -1
3. Next, get the pageID of the SCPF result page just generated, and run this job again with `SCPF_page_id` as the known pageID to generate **SCPF individual result pages**.
    - `top_level_page_id`: -1
    - `SCPF_page_id`: *page ID of SCPF result page*
    - `USECASE_page_id`: -1
4. Finally, get the pageID of the USECASE result page, and run this job again with `USECASE_page_id` as the known pageID to generate the **SR results page**.
    - `top_level_page_id`: -1
    - `SCPF_page_id`: -1
    - `USECASE_page_id`: *page ID of USECASE result page*


### [generateWikiTestList](https://jenkins.onosproject.org/view/QA/job/generate_automated_schedule_wiki/)
`generateWikiTestList.groovy` creates the [automated test schedule](https://wiki.onosproject.org/display/ONOS/Automated+Test+Schedule) on the ONOS wiki. The script reads from `JenkinsTestONTests.groovy` and creates a timetable for all tests in `tests.json`.

### [Overall_Graph_Generator](https://jenkins.onosproject.org/view/QA/job/manual-graph-generator-overall/)
`Overall_Graph_Generator` refreshes the overall graphs on the ONOS wiki. This script performs similar steps as the ending of the `master-trigger` script.

### [CHO_Graph_Generator](https://jenkins.onosproject.org/view/QA/job/graph-generator-CHO/)
`CHO_Graph_Generator` refreshes the CHO graphs on the ONOS wiki.

# Dependencies

### JenkinsGraphs

This script contains functions related to posting/retrieving from database, generating any type of wiki graph, and triggering the downstream `postjob` to publish the graphs.

### JenkinsPathAndFiles

This small script contains the paths for Jenkins workspaces and R script locations.  Paths are obtained from `paths.json`.

### JenkinsTestONTests

This script contains methods for retrieving tests, branches, schedules, and node labels. `tests.json`, `branches.json`, and `schedules.json` are initially read and are organized as `dict` format.

### PerformanceFuncs

This script contains methods similar to `JenkinsGraphs`, but are tailored towards SCPF related tests.
