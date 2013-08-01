/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package tai_ofa;

/**
 *
 * @author Raghavkashyap (raghavkashyap@paxterra.com)

	
 *   TestON is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation, either version 2 of the License, or
 *   (at your option) any later version.

 *   TestON is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.

 *   You should have received a copy of the GNU General Public License
 *   along with TestON.  If not, see <http://www.gnu.org/licenses/>.

 */
// Import the Java classes
import com.sun.javafx.scene.layout.region.BackgroundFill;
import com.sun.org.apache.bcel.internal.generic.LoadInstruction;
import java.awt.TextArea;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.io.*;
import java.net.MalformedURLException;
import java.nio.file.WatchService;
import java.text.SimpleDateFormat;
import java.util.logging.Level;
import java.util.logging.Logger;
import javafx.application.Platform;
import javafx.beans.value.ChangeListener;
import javafx.beans.value.ObservableValue;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.event.EventHandler;
import javafx.geometry.Insets;
import javafx.scene.chart.PieChart;
import javafx.scene.control.Button;
import javafx.scene.control.CheckBox;
import javafx.scene.control.Label;
import javafx.scene.control.Tab;
import javafx.scene.control.TabPane;
import javafx.scene.control.TableView;
import javafx.scene.control.TextAreaBuilder;
import javafx.scene.effect.BlendMode;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.input.ScrollEvent;
import javafx.scene.layout.HBox;
import javafx.scene.layout.StackPane;
import javafx.scene.paint.Color;
import javafx.scene.paint.Paint;
import javafx.stage.Popup;
import javafx.stage.Stage;
import org.apache.xmlrpc.XmlRpcClient;
import org.apache.xmlrpc.XmlRpcException;

public class ExecuteTest {

    Pattern stepPatt, casePatt, resultPatt, namePatt, summaryPatt, testStartPatt, testEndPatt, testExecutionTimePatt, testsPlannedPatt,
            testsRunPatt, totalPassPatt, totalFailPatt, noResultPatt, totalAbortPatt, execPercentagePatt, successPercentagePatt, assertionPatt, totalreRun;
    TableView summaryTable, finalSummaryTable, stepTable;
    public static int noOfPassed = 0, noOfFailed = 0, noOfAborted = 0, noOfNoResult = 0, failed = 0, passed = 0, noResults = 0, aboarted = 0;
    String summary, testStart, testEnd, testExecutionTime, testsPlanned, testsRun, totalPass,
            totalFail, noResult, totalAbort, execPercentage, successPercentage;
    ObservableList<SummaryTable> data;
    ObservableList<FinalSummaryTable> finalSummaryData;
    ObservableList<StepTable> stepSummaryData;
    //AutoMateTestSummary summaryWindow ;
    StackPane summaryTableRoot;
    TreeMap<String, String> stepHash = new TreeMap<String, String>();
    TreeMap<String, String> caseNameHash = new TreeMap<String, String>();
    Matcher m;
    int tableIndex = -1;
    int stepTableIndex = -1;
    Runnable r3;
    Button viewLogsButton;
    PieChart summaryChart;
    PieChart.Data passData, failData, abortData, noResultData;
    String selectedTest;
    ObservableList<PieChart.Data> pieChartData;
    javafx.scene.control.TextArea compononetLogText = TextAreaBuilder.create().build();
    javafx.scene.control.TextArea flowVisorSessionText = TextAreaBuilder.create().build();
    javafx.scene.control.TextArea poxSessionText = TextAreaBuilder.create().build();
    javafx.scene.control.TextArea mininetSessionText = TextAreaBuilder.create().build();
    Label statusImage;
    TAILocale label = new TAILocale(Locale.ENGLISH);

    public ExecuteTest(TableView summary, ObservableList<SummaryTable> dataInstance,
            PieChart chart, TableView finalSummary, ObservableList<FinalSummaryTable> finalSummaryDataInstance,
            Button viewLogs, ObservableList<PieChart.Data> pieChartData,
            PieChart.Data passData, PieChart.Data failData, PieChart.Data abortData, PieChart.Data noResultData, String testName, javafx.scene.control.TextArea componentLogText,
            TableView stepTable, ObservableList<StepTable> stepTableData, javafx.scene.control.TextArea poxText, javafx.scene.control.TextArea mininetText, javafx.scene.control.TextArea flowText) {
        this.summaryTable = summary;
        data = dataInstance;
        summaryChart = chart;
        finalSummaryTable = finalSummary;
        finalSummaryData = finalSummaryDataInstance;
        viewLogsButton = viewLogs;
        this.pieChartData = pieChartData;
        this.passData = passData;
        this.failData = failData;
        this.abortData = abortData;
        this.noResultData = noResultData;
        this.selectedTest = testName;
        this.compononetLogText = componentLogText;
        this.stepTable = stepTable;
        this.stepSummaryData = stepTableData;
        this.poxSessionText = poxText;
        this.mininetSessionText = mininetText;
        this.flowVisorSessionText = flowText;

    }
    String currentTestCase, testCaseName, testCaseStatus, testCaseStartTime, testCaseEndTime;

    public void runTest() {



        try {

            summaryTable.setVisible(true);
            getCaseName();
            Iterator entries = caseNameHash.entrySet().iterator();
            data = FXCollections.observableArrayList();
            int index = 0;
            while (entries.hasNext()) {
                index++;
                Map.Entry entry = (Map.Entry) entries.next();
                String key = (String) entry.getKey();
                String value = (String) entry.getValue();
                Image image = new Image(getClass().getResourceAsStream("/images/loading.gif"), 10, 10, true, true);
                data.add(new SummaryTable(new Label(key), new Label(value), new Label("", new ImageView(image)), new Label(), new Label()));
            }
            summaryTable.setItems(data);
            File file = new File(selectedTest);
            String[] runThisFile = file.getName().split("\\.");
            try {
                XmlRpcClient server = new XmlRpcClient("http://localhost:9000");
                Vector params = new Vector();
                params.add(new String(selectedTest));
                final Object result = server.execute("runTest", params);
                new Thread(new Runnable() {
                    @Override
                    public void run() {
                        ProcessBuilder header = new ProcessBuilder("/bin/sh", "-c", "head -20 " + result.toString());
                        Process headProcess;
                        try {
                            headProcess = header.start();
                            BufferedReader inputHeader = new BufferedReader(new InputStreamReader(headProcess.getInputStream()));
                            String lines;
                            String totalText = "";
                            while ((lines = inputHeader.readLine()) != null) {
                                try {
                                    totalText = totalText + "\n" + lines;
                                    updateData(lines);
                                } catch (Exception e) {
                                }
                            }
                            compononetLogText.appendText(totalText);
                            headProcess.destroy();
                        } catch (IOException ex) {
                            Logger.getLogger(ExecuteTest.class.getName()).log(Level.SEVERE, null, ex);
                        }
                        String command = "tail -f " + result.toString();
                        File dir = new File(result.toString());
                        String parentPath = dir.getParent();
                        ProcessBuilder tail = new ProcessBuilder("/bin/sh", "-c", "tail -f " + result.toString());
                        Process process;
                        int nullcount = 0;
                        try {
                            while (true) {
                                process = tail.start();
                                BufferedReader input = new BufferedReader(new InputStreamReader(process.getInputStream()));
                                String line;
                                try {
                                    while ((line = input.readLine()) != null) {
                                        compononetLogText.appendText("\n" + line + "\n");
                                        updateData(line);
                                    }
                                    if (input.readLine() == null) {
                                        nullcount++;
                                    }
                                    if (nullcount == 2) {
                                        process.destroy();
                                    }

                                } catch (Exception e) {
                                }
                            }
                        } catch (IOException ex) {
                            Logger.getLogger(ExecuteTest.class.getName()).log(Level.SEVERE, null, ex);
                        }
                        String poxFileName = parentPath + "/" + "POX2.session";
                        String flowFileName = parentPath + "/" + "FlowVisor1.session";
                        String mininetFileName = parentPath + "/" + "Mininet1.session";
                        ProcessBuilder tailpox = new ProcessBuilder("/bin/sh", "-c", "tail -f " + poxFileName);
                    }
                }).start();

                r3 = new Runnable() {
                    public void run() {
                        try {
                            summaryChart.setVisible(true);
                            try {
                                pieChartData.set(0, new PieChart.Data("Pass", ExecuteTest.noOfPassed));
                                pieChartData.set(1, new PieChart.Data("Fail", ExecuteTest.noOfFailed));
                                pieChartData.set(2, new PieChart.Data("Abort", ExecuteTest.noOfAborted));
                                passData.setPieValue(1);
                                failData.setPieValue(0);
                                abortData.setPieValue(0);
                                noResultData.setPieValue(0);
                                summaryChart.getStylesheets().add(getClass().getResource("test.css").toExternalForm());
                                summaryChart.setData(pieChartData);
                            } catch (Exception e) {
                                e.printStackTrace();
                            }
                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                    }
                };
            } catch (Exception e) {
                e.printStackTrace();
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void updateData(String line) {

        casePatt = Pattern.compile("\\s*Result\\s+summary\\s+for\\s+Testcase(\\d+)");
        m = casePatt.matcher(line);
        if (m.find()) {
            Date dNow = new Date();
            SimpleDateFormat ft = new SimpleDateFormat("hh:mm:ss a zzz dd.MM.yyyy");
            testCaseStartTime = ft.format(dNow);
            currentTestCase = m.group(1);
            stepHash.clear();
            getTestSteps(m.group(1));
            Image image = new Image(getClass().getResourceAsStream("/images/loading.gif"), 10, 10, true, true);
            Label statusImage = new Label("", new ImageView(image));
            stepSummaryData = FXCollections.observableArrayList(new StepTable(new Label(""), new Label(""), new Label("")));
            Iterator entries = stepHash.entrySet().iterator();
            while (entries.hasNext()) {
                Map.Entry entry = (Map.Entry) entries.next();
                String key = (String) entry.getKey();
                String value = (String) entry.getValue();
                stepSummaryData.add(new StepTable(new Label(key), new Label(value), new Label("", new ImageView(image))));
            }
            stepTable.setItems(stepSummaryData);
        }

        namePatt = Pattern.compile("\\[(.*)\\]\\s*\\[(.*)\\]\\s*\\[\\s*CASE\\s*\\](.*)\\s*");
        m = namePatt.matcher(line);

        if (m.find()) {
            testCaseName = m.group(3);
            Image image = new Image(getClass().getResourceAsStream("/images/progress.png"));
            statusImage = new Label("", new ImageView(image));
            if (tableIndex < 0) {
                data = FXCollections.observableArrayList(new SummaryTable(new Label(currentTestCase), new Label(testCaseName),
                        statusImage, new Label(testCaseStartTime), new Label()));
            } else {
                data.add(new SummaryTable(new Label(currentTestCase), new Label(testCaseName), statusImage,
                        new Label(testCaseStartTime), new Label("")));
            }
            tableIndex++;
        }

        stepPatt = Pattern.compile("\\[(.*)\\]\\s*\\[(.*)\\]\\s*\\[\\s*STEP\\s*\\]\\s*(\\d+)\\.(\\d+):(.*)\\s*");

        m = stepPatt.matcher(line);
        if (m.find()) {
            String currentStepNumber = m.group(3) + "." + m.group(4);
            for (int i = 1; i < stepSummaryData.size(); i++) {
                if (stepSummaryData.get(i).getTestStepId().getText().equals(currentStepNumber)) {
                    Image image = new Image(getClass().getResourceAsStream("/images/progress.png"));
                    stepTableIndex = i;
                    stepSummaryData.set(i, new StepTable(new Label(stepSummaryData.get(i).getTestStepId().getText()), new Label(stepSummaryData.get(i).getTestStepName().getText()), new Label("", new ImageView(image))));
                    Image images = new Image(getClass().getResourceAsStream("/images/Pass_Icon.png"));
                }
            }

        }

        assertionPatt = Pattern.compile("\\s*(.*)\\s*-\\s*(\\w+)\\s*-\\s*(\\w+)\\s*-\\s*(.*)\\s*");
        m = assertionPatt.matcher(line);
        if (m.find() && stepTableIndex > -1) {
            if (m.group(3).equals("INFO") && m.group(4).equals("Assertion Passed")) {
                Image image = new Image(getClass().getResourceAsStream("/images/Pass_Icon.png"));
                stepSummaryData.set(stepTableIndex, new StepTable(new Label(stepSummaryData.get(stepTableIndex).getTestStepId().getText()),
                        new Label(stepSummaryData.get(stepTableIndex).getTestStepName().getText()), new Label("", new ImageView(image))));
            } else if (m.group(3).equals("WARNING") && m.group(4).equals("Assertion Failed")) {
                Image image = new Image(getClass().getResourceAsStream("/images/Fail_Icon.png"));
                stepSummaryData.set(stepTableIndex, new StepTable(new Label(stepSummaryData.get(stepTableIndex).getTestStepId().getText()),
                        new Label(stepSummaryData.get(stepTableIndex).getTestStepName().getText()), new Label("", new ImageView(image))));
                XmlRpcClient server;
            }

        }

        resultPatt = Pattern.compile("\\s*Result:\\s+(\\w+)\\s*");
        m = resultPatt.matcher(line);
        if (m.find()) {
            testCaseStatus = m.group(1);
            Date dNow = new Date();
            Image image;
            SimpleDateFormat ft = new SimpleDateFormat("hh:mm:ss a zzz dd.MM.yyyy");
            testCaseEndTime = ft.format(dNow);
            if (testCaseStatus.equalsIgnoreCase("No result")) {
                image = new Image(getClass().getResourceAsStream("/images/noResult.png"));
                statusImage = new Label("", new ImageView(image));;
                ExecuteTest.noOfNoResult++;
            }

            if (testCaseStatus.equalsIgnoreCase("Pass")) {
                image = new Image(getClass().getResourceAsStream("/images/Pass_Icon.png"));
                statusImage = new Label("", new ImageView(image));
                ExecuteTest.noOfPassed++;
            }
            if (testCaseStatus.equals("Failed")) {
                image = new Image(getClass().getResourceAsStream("/images/Fail_Icon.png"));
                statusImage = new Label("", new ImageView(image));
                ExecuteTest.noOfFailed++;
            } else if (testCaseStatus.equals("Aborted")) {
                image = new Image(getClass().getResourceAsStream("/images/Abort_Icon.png"));
                statusImage = new Label("", new ImageView(image));
                this.noOfAborted++;
            }
            data.set(tableIndex, new SummaryTable(new Label(currentTestCase), new Label(testCaseName),
                    statusImage, new Label(testCaseStartTime), new Label(testCaseEndTime)));
            summaryTable.setItems(data);
        }

        summaryPatt = Pattern.compile("\\s*Test+\\s+Execution(.*)");
        m = summaryPatt.matcher(line);
        if (m.find()) {
        }

        testStartPatt = Pattern.compile("Test\\s+Start\\s+\\:\\s+(.*)");
        m = testStartPatt.matcher(line);
        if (m.find()) {
            Image image = new Image(getClass().getResourceAsStream("/images/Pass_Icon.png"));
            statusImage = new Label("", new ImageView(image));
            data.set(tableIndex, new SummaryTable(new Label(currentTestCase), new Label(testCaseName),
                    statusImage, new Label(testCaseStartTime), new Label(testCaseEndTime)));
            stepTable.setVisible(false);
            finalSummaryTable.setVisible(true);
            summaryChart.setVisible(true);
            finalSummaryData = FXCollections.observableArrayList(new FinalSummaryTable(new Label(""), new Label("")));
            finalSummaryTable.setItems(finalSummaryData);
            testStart = m.group(1);
            finalSummaryData.set(0, new FinalSummaryTable(new Label("Test Start"), new Label(testStart)));
            finalSummaryTable.setItems(finalSummaryData);
        }
        testEndPatt = Pattern.compile("Test\\s+End\\s+\\:\\s+(.*)");
        m = testEndPatt.matcher(line);
        if (m.find()) {
            testEnd = m.group(1);
            finalSummaryData.add(new FinalSummaryTable(new Label("Test End"), new Label(testEnd)));
            finalSummaryTable.setItems(finalSummaryData);
        }
        testExecutionTimePatt = Pattern.compile("\\s*Execution\\s+Time\\s+\\:\\s+(.*)");
        m = testExecutionTimePatt.matcher(line);
        if (m.find()) {
            testExecutionTime = m.group(1);
            finalSummaryData.add(new FinalSummaryTable(new Label("Execution Time"), new Label(testExecutionTime)));
            finalSummaryTable.setItems(finalSummaryData);
        }
        testsPlannedPatt = Pattern.compile("\\s*Total\\s+tests\\s+planned\\s+\\:\\s*(.*)");
        m = testsPlannedPatt.matcher(line);
        if (m.find()) {
            testsPlanned = m.group(1);
            finalSummaryData.add(new FinalSummaryTable(new Label("Total Tests Planned"), new Label(testsPlanned)));
            finalSummaryTable.setItems(finalSummaryData);
        }

        testsRunPatt = Pattern.compile("\\s*Total\\s+tests\\s+Run\\s+\\:\\s+(.*)");
        m = testsRunPatt.matcher(line);
        if (m.find()) {
            testsRun = m.group(1);
            finalSummaryData.add(new FinalSummaryTable(new Label("Total Tests Run"), new Label(testsRun)));
            finalSummaryTable.setItems(finalSummaryData);
        }
        totalPassPatt = Pattern.compile("Total\\s+Pass\\s+\\:\\s+(.*)");
        m = totalPassPatt.matcher(line);
        if (m.find()) {
            totalPass = m.group(1);
            Label totalPassL = new Label("Total Pass");
            totalPassL.setTextFill(Color.GREEN);
            totalPassL.setStyle("-fx-font-weight: bold");
            Label totalPassValue = new Label(totalPass);
            totalPassValue.setTextFill(Color.GREEN);
            totalPassValue.setStyle("-fx-font-weight: bold");
            finalSummaryData.add(new FinalSummaryTable(totalPassL, totalPassValue));
            finalSummaryTable.setItems(finalSummaryData);
        }
        totalFailPatt = Pattern.compile("Total\\s+Fail\\s+\\:\\s+(.*)");
        m = totalFailPatt.matcher(line);
        if (m.find()) {
            totalFail = m.group(1);
            Label totalFailL = new Label("Total Fail");
            totalFailL.setTextFill(Color.RED);
            totalFailL.setStyle("-fx-font-weight: bold");
            Label totalFailValue = new Label(totalFail);
            totalFailValue.setTextFill(Color.RED);
            totalFailValue.setStyle("-fx-font-weight: bold");
            finalSummaryData.add(new FinalSummaryTable(totalFailL, totalFailValue));
            finalSummaryTable.setItems(finalSummaryData);
        }

        totalreRun = Pattern.compile("Total\\s+Re\\-Run\\s+\\:\\s+(.*)");
        m = totalreRun.matcher(line);
        if (m.find()) {
            Label totalReRun = new Label("Total Re-Run");
            totalReRun.setTextFill(Color.BLUE);
            totalReRun.setStyle("-fx-font-weight: bold");
            Label totalReRunValue = new Label(m.group(1));
            totalReRunValue.setTextFill(Color.BLUE);
            totalReRunValue.setStyle("-fx-font-weight: bold");
            finalSummaryData.add(new FinalSummaryTable(totalReRun, totalReRunValue));
            finalSummaryTable.setItems(finalSummaryData);
        }

        noResultPatt = Pattern.compile("Total\\s+No\\s+Result\\s+\\:\\s+(.*)");
        m = noResultPatt.matcher(line);
        if (m.find()) {
            noResult = m.group(1);
            finalSummaryData.add(new FinalSummaryTable(new Label("Total No-Result"), new Label(noResult)));
            finalSummaryTable.setItems(finalSummaryData);
        }

        totalAbortPatt = Pattern.compile("Total\\sabort\\s+\\:\\s+(.*)");
        m = totalAbortPatt.matcher(line);
        if (m.find()) {
            totalAbort = m.group(1);
            finalSummaryData.add(new FinalSummaryTable(new Label("Total Abort"), new Label(totalAbort)));
            finalSummaryTable.setItems(finalSummaryData);
        }
        execPercentagePatt = Pattern.compile("Execution\\s+Result\\s+\\:\\s+(.*)");
        m = execPercentagePatt.matcher(line);
        if (m.find()) {
            execPercentage = m.group(1);
            finalSummaryData.add(new FinalSummaryTable(new Label("Execution Percentage"), new Label(execPercentage)));
            finalSummaryTable.setItems(finalSummaryData);
            Platform.runLater(r3);
        }
        successPercentagePatt = Pattern.compile("Success\\s+Percentage\\s+\\:\\s+(.*)");
        m = successPercentagePatt.matcher(line);
        if (m.find()) {
            successPercentage = m.group(1);
            finalSummaryData.add(new FinalSummaryTable(new Label("Success Percentage"), new Label(successPercentage)));
            finalSummaryTable.setItems(finalSummaryData);
        }
    }

    public ExecuteTest() {
    }

    public String getTestCase() {
        return currentTestCase;
    }

    public void getTestSteps(String caseNumber) {
        OFAFileOperations fileOperation = new OFAFileOperations();
        int stepCount = 0;
        String stepCounter = "";
        String ospkFileName = label.hierarchyTestON + "/tests/" + selectedTest + "/" + selectedTest + ".ospk";
        String pythonScriptName = label.hierarchyTestON + "/tests/" + selectedTest + "/" + selectedTest + ".py";
        BufferedReader input = null;
        ArrayList<String> contents = new ArrayList<String>();
        File scriptName = new File(ospkFileName);
        if (scriptName.exists()) {
            try {
                //use buffering, reading one line at a time
                //FileReader always assumes default encoding is OK!
                try {
                    input = new BufferedReader(new FileReader(scriptName));
                } catch (Exception e) {
                }

                try {
                    String line = null; //not declared within while loop
                    while ((line = input.readLine()) != null) {
                        contents.add(line);
                    }
                } finally {
                    try {
                        input.close();
                    } catch (Exception e) {
                    }
                }
            } catch (IOException ex) {
                ex.printStackTrace();
            }
            for (int i = 0; i < contents.size(); i++) {
                Pattern casePattern = Pattern.compile("\\s*CASE\\s*(\\d+)\\s*");
                Matcher caseMatcher = casePattern.matcher(contents.get(i));
                if (caseMatcher.find()) {
                    if (caseMatcher.group(1).equals(caseNumber)) {
                        i++;
                        Pattern casePatterns = Pattern.compile("\\s*CASE\\s*(\\d+)\\s*");
                        Matcher caseMatchers = casePatterns.matcher(contents.get(i));
                        while (!caseMatchers.find() && i < contents.size()) {
                            Pattern casesPatterns = Pattern.compile("\\s*CASE\\s*(\\d+)\\s*");
                            Matcher casesMatchers = casesPatterns.matcher(contents.get(i));
                            if (casesMatchers.find()) {
                                break;
                            } else {
                                Pattern stepPattern = Pattern.compile("\\s*STEP\\s+\"\\s*(.*)\\s*\"\\s*");
                                Matcher stepMatcher = stepPattern.matcher(contents.get(i));
                                try {
                                    if (stepMatcher.find()) {
                                        stepCount++;
                                        stepCounter = caseNumber + "." + String.valueOf(stepCount);
                                        stepHash.put(stepCounter, stepMatcher.group(1));
                                    }
                                } catch (Exception e) {
                                    break;
                                }
                                i++;
                            }

                        }
                        i--;
                    }

                }
            }
        } else {
            try {
                //use buffering, reading one line at a time
                //FileReader always assumes default encoding is OK!
                try {
                    input = new BufferedReader(new FileReader(pythonScriptName));

                } catch (Exception e) {
                }

                try {
                    String line = null; //not declared within while loop

                    while ((line = input.readLine()) != null) {
                        contents.add(line);
                    }
                } finally {
                    try {
                        input.close();
                    } catch (Exception e) {
                    }

                }
            } catch (IOException ex) {
                ex.printStackTrace();
            }

            for (int i = 0; i < contents.size(); i++) {
                Pattern casePattern = Pattern.compile("\\s*def\\s+CASE(\\d+)\\s*\\(\\s*(.*)\\s*\\)\\s*:\\s*");
                Matcher caseMatcher = casePattern.matcher(contents.get(i));
                if (caseMatcher.find()) {
                    if (caseMatcher.group(1).equals(caseNumber)) {
                        i++;
                        Pattern casePatterns = Pattern.compile("\\s*def\\s+CASE(\\d+)\\s*\\(\\s*(.*)\\s*\\)\\s*:\\s*");
                        Matcher caseMatchers = casePatterns.matcher(contents.get(i));
                        while (!caseMatchers.find() && i < contents.size()) {
                            Pattern casesPatterns = Pattern.compile("\\s*def\\s+CASE(\\d+)\\s*\\(\\s*(.*)\\s*\\)\\s*:\\s*");
                            Matcher casesMatchers = casesPatterns.matcher(contents.get(i));
                            if (casesMatchers.find()) {
                                break;
                            } else {
                                Pattern stepPattern = Pattern.compile("\\s*main.step\\(\\s*\"\\s*(.*)\\s*\"\\s*\\)\\s*");
                                Matcher stepMatcher = stepPattern.matcher(contents.get(i));
                                try {
                                    if (stepMatcher.find()) {
                                        stepCount++;
                                        stepCounter = caseNumber + "." + String.valueOf(stepCount);
                                        stepHash.put(stepCounter, stepMatcher.group(1));
                                    }
                                } catch (Exception e) {
                                    break;
                                }
                                i++;
                            }
                        }
                        i--;
                    }
                }
            }
        }
    }

    public void getCaseName() {
        int stepCount = 0;
        String stepCounter = "";
        String paramFilePath = label.hierarchyTestON + "/tests/" + selectedTest + "/" + selectedTest + ".params";
        FileInputStream fstream;
        String testCases = "";
        ArrayList<String> paramFileName = new ArrayList<String>();
        ArrayList<String> nameBetweenTags = new ArrayList<String>();
        try {
            fstream = new FileInputStream(paramFilePath);
            DataInputStream in = new DataInputStream(fstream);
            BufferedReader br = new BufferedReader(new InputStreamReader(in));
            String strLine;
            try {
                while ((strLine = br.readLine()) != null) {
                    paramFileName.add(strLine);
                }
            } catch (IOException ex) {
                Logger.getLogger(ExecuteTest.class.getName()).log(Level.SEVERE, null, ex);
            }
        } catch (FileNotFoundException ex) {
            Logger.getLogger(ExecuteTest.class.getName()).log(Level.SEVERE, null, ex);
        }

        for (int index = 0; index < paramFileName.size(); index++) {
            Pattern testsPattern = Pattern.compile("<testcases>\\s*(.*)\\s*</testcases>");
            Matcher testMatcher = testsPattern.matcher(paramFileName.get(index));
            if (testMatcher.find()) {
                testCases = testMatcher.group(1);
                testCases = testCases.replaceAll(" ", "");
            }

        }

        String[] testArray = null;
        testArray = testCases.split(",");
        String ospkFileName = label.hierarchyTestON + "/tests/" + selectedTest + "/" + selectedTest + ".ospk";
        String pythonScriptName = label.hierarchyTestON + "/tests/" + selectedTest + "/" + selectedTest + ".py";
        BufferedReader input = null;
        ArrayList<String> contents = new ArrayList<String>();
        File scriptName = new File(ospkFileName);
        String caseId = "";
        String caseName = "";
        if (scriptName.exists()) {
            try {
                FileInputStream fstream1 = new FileInputStream(ospkFileName);
                ArrayList<String> driverFunctionName = new ArrayList<String>();
                DataInputStream in = new DataInputStream(fstream1);
                BufferedReader br = new BufferedReader(new InputStreamReader(in));
                String strLine;
                while ((strLine = br.readLine()) != null) {
                    Pattern casePattern = Pattern.compile("^CASE\\s+(\\d+)");
                    Matcher match = casePattern.matcher(strLine);
                    while (match.find()) {
                        driverFunctionName.add(match.group());
                        caseId = match.group(1);
                        strLine = br.readLine();
                        casePattern = Pattern.compile("NAME\\s+(\\\"+(.*)\\\")");
                        match = casePattern.matcher(strLine);
                        if (match.find()) {
                            caseName = match.group(2);
                        }
                        caseNameHash.put(caseId, caseName);
                    }
                }
            } catch (Exception e) {
            }
        } else {
            try {

                FileInputStream fstream2 = new FileInputStream(pythonScriptName);
                ArrayList<String> driverFunctionName = new ArrayList<String>();
                DataInputStream in = new DataInputStream(fstream2);
                BufferedReader br = new BufferedReader(new InputStreamReader(in));
                String strLine;
                while ((strLine = br.readLine()) != null) {
                    Pattern casePattern = Pattern.compile("\\s*def\\s+CASE(\\d+)\\s*\\(\\s*(.*)\\s*\\)\\s*:\\s*");
                    Matcher match = casePattern.matcher(strLine);
                    if (match.find()) {
                        driverFunctionName.add(match.group());
                        if (Arrays.asList(testArray).contains(match.group(1))) {
                            caseId = match.group(1);
                        } else {
                            caseId = null;
                        }
                        strLine = br.readLine();
                    }

                    casePattern = Pattern.compile("\\s*main.case\\(\\s*\"\\s*(.*)\\s*\"\\s*\\)\\s*");
                    match = casePattern.matcher(strLine);

                    if (match.find()) {
                        caseName = match.group(1);
                        if (caseId != null) {
                            caseNameHash.put(caseId, caseName);
                        }
                    }
                }
            } catch (Exception e) {
            }
        }
    }
}
