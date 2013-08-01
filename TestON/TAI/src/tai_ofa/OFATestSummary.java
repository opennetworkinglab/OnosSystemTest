/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package tai_ofa;

import com.sun.org.apache.xalan.internal.xsltc.compiler.util.StringStack;
import java.awt.Color;
import java.awt.TextArea;
import java.io.IOException;
import java.net.MalformedURLException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Vector;
import java.util.logging.Level;
import java.util.logging.Logger;
import javafx.application.Application;
import javafx.beans.value.ChangeListener;
import javafx.beans.value.ObservableValue;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.geometry.Insets;
import javafx.geometry.Orientation;
import javafx.scene.Group;
import javafx.scene.Scene;
import javafx.scene.chart.PieChart;
import javafx.scene.control.Button;
import javafx.scene.control.CheckBox;
import javafx.scene.control.ComboBox;
import javafx.scene.control.ComboBoxBuilder;
import javafx.scene.control.Label;
import javafx.scene.control.Separator;
import javafx.scene.control.SplitPane;
import javafx.scene.control.Tab;
import javafx.scene.control.TabPane;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableView;
import javafx.scene.control.TextAreaBuilder;
import javafx.scene.control.TextField;
import javafx.scene.control.TextFieldBuilder;
import javafx.scene.control.ToolBar;
import javafx.scene.control.Tooltip;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.layout.FlowPane;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.Pane;
import javafx.scene.layout.StackPane;
import javafx.scene.layout.VBox;
import javafx.scene.text.Text;
import javafx.stage.Stage;
import javafx.stage.WindowEvent;
import org.apache.xmlrpc.XmlRpcClient;
import org.apache.xmlrpc.XmlRpcException;

/**
 *
 * @author Raghav Kashyap (raghavkashyap@paxterrasolutions.com)
	
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
public class OFATestSummary extends Application {

    ObservableList<SummaryTable> data;
    ObservableList<FinalSummaryTable> summaryData;
    ObservableList<StepTable> stepData;
    TableView<SummaryTable> summaryTable;
    TableView<StepTable> stepTable;
    PieChart.Data passData = new PieChart.Data("Pass", 0);
    PieChart.Data failData = new PieChart.Data("Fail", 0);
    PieChart.Data abortData = new PieChart.Data("Abort", 0);
    PieChart.Data noResult = new PieChart.Data("No Result", 0);
    ObservableList<PieChart.Data> pieChartData;
    TableView<FinalSummaryTable> finalSummaryTable = new TableView<FinalSummaryTable>();
    TableColumn testCaseIdColumn, testCaseNameColumn;
    TableColumn testCaseStatusColumn, testCaseStartTimeColumn, testCaseEndTimeColumn;
    Button viewLogs = new Button("Debug & Console");
    GridPane buttonPane = new GridPane();
    TableColumn stepId, stepName, stepStatus;
    TableColumn summaryItem, information;
    HashMap<String, String> testCaseIdAndName = new HashMap<String, String>();
    String caseId, caseName;
    Stage copyStage;
    PieChart chart;
    StackPane rootStack;
    TAI_OFA ofaReference;
    Stage paramaterWindow;
    ComboBox LogBox;
    TabPane execWindow = new TabPane();
    Tab debugLog = new Tab("Debug Logs");
    Tab componentLog = new Tab("Test Log");
    Tab testSummaryTab = new Tab("Test Summary");
    Tab dpctlSessionTab = new Tab("FlowVisor1.session");
    Tab mininetSessionTab = new Tab("Mininet1.session");
    Tab poxSessionTab = new Tab("POX2.session");
    TabPane baseTabPane = new TabPane();
    javafx.scene.control.TextArea debugLogText = TextAreaBuilder.create().build();
    javafx.scene.control.TextArea compononetLogText = TextAreaBuilder.create().build();
    javafx.scene.control.TextArea flowVisorSessionText = TextAreaBuilder.create().build();
    javafx.scene.control.TextArea poxSessionText = TextAreaBuilder.create().build();
    javafx.scene.control.TextArea mininetSessionText = TextAreaBuilder.create().build();
    String variableName = "";
    String command = "";
    ToolBar quickLauchBar = new ToolBar();
    Double toolBarHeight;
    Scene scene;
    SplitPane baseSplitPane = new SplitPane();
    TabPane consoleTabPane;

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        launch(args);
    }

    public OFATestSummary(TAI_OFA ofaReference, Stage paramaterWindow) {
        this.ofaReference = ofaReference;
        this.paramaterWindow = paramaterWindow;
    }

    public void start(Stage primaryStage) {
        copyStage = primaryStage;
        primaryStage.setTitle("Test Execution Status");
        primaryStage.setResizable(false);
        Group rootGroup = new Group();
        scene = new Scene(rootGroup, 1020, 920);
        Pane basePanel = new Pane();
        HBox baseBox = new HBox();
        VBox consoleBox = new VBox();
        VBox buttonBox = new VBox();

        getDebugTab();
        getToolBar();
        buttonBox.getChildren().addAll(buttonPane);
        consoleBox.getChildren().addAll(quickLauchBar, baseTabPane);
        baseBox.getChildren().addAll(consoleBox);
        basePanel.getChildren().addAll(baseBox);
        SplitPane sp = getTestSummary();
        testSummaryTab.setContent(sp);
        testSummaryTab.setClosable(false);
        baseTabPane.getTabs().addAll(testSummaryTab);
        javafx.scene.control.SingleSelectionModel<Tab> selectionModel = baseTabPane.getSelectionModel();
        selectionModel.select(testSummaryTab);
        baseTabPane.prefWidthProperty().bind(scene.widthProperty().subtract(200));
        baseTabPane.prefHeightProperty().bind(scene.heightProperty().subtract(10));
        primaryStage.setOnCloseRequest(new EventHandler<WindowEvent>() {
            @Override
            public void handle(WindowEvent t) {
                XmlRpcClient server;
                try {
                    server = new XmlRpcClient("http://localhost:9000");
                    Vector params = new Vector();
                    params.add(new String("main"));
                    try {
                        server.execute("stop", new Vector());
                    } catch (XmlRpcException ex) {
                        Logger.getLogger(OFATestSummary.class.getName()).log(Level.SEVERE, null, ex);
                    } catch (IOException ex) {
                        Logger.getLogger(OFATestSummary.class.getName()).log(Level.SEVERE, null, ex);
                    }
                } catch (MalformedURLException ex) {
                    Logger.getLogger(OFATestSummary.class.getName()).log(Level.SEVERE, null, ex);
                }
            }
        });

        basePanel.prefHeightProperty().bind(scene.heightProperty());
        quickLauchBar.prefWidthProperty().bind(scene.widthProperty());
        quickLauchBar.setMinHeight(scene.heightProperty().get() / 20);
        toolBarHeight = quickLauchBar.getMinHeight();
        baseTabPane.prefHeightProperty().bind(scene.heightProperty());
        baseBox.prefHeightProperty().bind(scene.heightProperty());
        consoleBox.prefHeightProperty().bind(scene.heightProperty());
        rootGroup.getChildren().addAll(basePanel);
        primaryStage.setScene(scene);
        primaryStage.show();

    }

    public TableView getTable() {
        return summaryTable;
    }

    public SplitPane getTestSummary() {
        GridPane testCaseSummaryTable = new GridPane();
        testCaseSummaryTable.setPadding(new Insets(10, 0, 0, 10));
        GridPane finalSummaryPane = new GridPane();
        finalSummaryPane.setPadding(new Insets(300, 0, 0, 20));
        GridPane stepSummaryPane = new GridPane();
        stepSummaryPane.setPadding(new Insets(300, 0, 0, 20));

        CheckBox selectTestCase = new CheckBox();
        summaryTable = new TableView<SummaryTable>();
        stepTable = new TableView<StepTable>();
        summaryTable.setMinWidth(580);
        summaryTable.setMaxHeight(250);
        testCaseIdColumn = new TableColumn(ofaReference.label.testSummaryTestCaseId);
        testCaseIdColumn.setCellValueFactory(new PropertyValueFactory<SummaryTable, Label>("testCaseId"));
        testCaseIdColumn.setMaxWidth(30);
        testCaseIdColumn.setResizable(true);

        testCaseNameColumn = new TableColumn(ofaReference.label.testSummaryTestCaseName);
        testCaseNameColumn.setCellValueFactory(new PropertyValueFactory<SummaryTable, Label>("testCaseName"));
        testCaseNameColumn.setMinWidth(303);
        testCaseNameColumn.setResizable(true);

        testCaseStatusColumn = new TableColumn(ofaReference.label.testSummaryExecutionStatus);
        testCaseStatusColumn.setCellValueFactory(new PropertyValueFactory<SummaryTable, Label>("testCaseStatus"));
        testCaseStatusColumn.setMinWidth(85);
        testCaseStatusColumn.setResizable(true);

        testCaseStartTimeColumn = new TableColumn(ofaReference.label.testSummaryStartTest);
        testCaseStartTimeColumn.setCellValueFactory(new PropertyValueFactory<SummaryTable, Label>("testCaseStartTime"));
        testCaseStartTimeColumn.setMinWidth(195);
        testCaseStartTimeColumn.setResizable(true);

        testCaseEndTimeColumn = new TableColumn(ofaReference.label.testSummaryEndTest);
        testCaseEndTimeColumn.setCellValueFactory(new PropertyValueFactory<SummaryTable, Label>("testCaseEndTime"));
        testCaseEndTimeColumn.setMinWidth(195);
        testCaseEndTimeColumn.setResizable(true);

        summaryTable.setItems(data);
        summaryTable.getColumns().addAll(testCaseIdColumn, testCaseNameColumn, testCaseStatusColumn, testCaseStartTimeColumn, testCaseEndTimeColumn);

        summaryItem = new TableColumn(ofaReference.label.summary);
        summaryItem.setCellValueFactory(new PropertyValueFactory<SummaryTable, Label>("summaryItem"));
        summaryItem.setMinWidth(140);
        summaryItem.setResizable(true);

        information = new TableColumn(ofaReference.label.information);
        information.setCellValueFactory(new PropertyValueFactory<SummaryTable, Label>("information"));
        information.setMinWidth(210);
        information.setResizable(true);

        finalSummaryTable.setMinWidth(350);
        finalSummaryTable.setMaxHeight(300);
        SplitPane leftPane = new SplitPane();
        SplitPane rightPane = new SplitPane();
        leftPane.setOrientation(Orientation.HORIZONTAL);
        rightPane.setOrientation(Orientation.VERTICAL);
        finalSummaryTable.setItems(summaryData);
        finalSummaryTable.setVisible(false);
        finalSummaryTable.getColumns().addAll(summaryItem, information);
        HBox pieChart = new HBox(10);
        pieChart.setPadding(new Insets(300, 0, 0, 300));
        ArrayList<PieChart.Data> dataList = new ArrayList<PieChart.Data>();

        dataList.add(passData);
        dataList.add(failData);
        dataList.add(abortData);
        dataList.add(noResult);
        pieChartData = FXCollections.observableArrayList(dataList);
        chart = new PieChart(pieChartData);
        chart.setTitle(ofaReference.label.testSummaryTestSummary);
        pieChart.getChildren().add(chart);
        chart.setVisible(false);
        summaryTable.setVisible(false);
        stepTable.setVisible(true);
        stepTable.setMinWidth(450);
        stepTable.setMaxHeight(300);

        stepId = new TableColumn("ID");
        stepId.setCellValueFactory(new PropertyValueFactory<StepTable, Label>("testStepId"));
        stepId.setMinWidth(10);
        stepId.setResizable(true);

        stepName = new TableColumn("Name");
        stepName.setCellValueFactory(new PropertyValueFactory<StepTable, Label>("testStepName"));
        stepName.setMinWidth(470);
        stepName.setResizable(true);

        stepStatus = new TableColumn("Status");
        stepStatus.setCellValueFactory(new PropertyValueFactory<StepTable, Label>("testStepStatus"));
        stepStatus.setMinWidth(40);
        stepStatus.setResizable(true);
        stepTable.getColumns().addAll(stepId, stepName, stepStatus);
        stepTable.setItems(stepData);
        stepSummaryPane.add(stepTable, 0, 2);

        finalSummaryPane.add(finalSummaryTable, 0, 2);
        rootStack = new StackPane();
        testCaseSummaryTable.add(summaryTable, 0, 1);
        rootStack.getChildren().addAll(testCaseSummaryTable, pieChart, stepSummaryPane, finalSummaryPane);
        leftPane.getItems().addAll(rootStack);
        consoleTabPane = new TabPane();
        consoleTabPane.setPrefWidth(700);
        consoleTabPane.getTabs().addAll(componentLog, debugLog, dpctlSessionTab, mininetSessionTab, poxSessionTab);

        Image topoImage = new Image("images/topo.png", 400, 200, true, true);
        ImageView topo = new ImageView(topoImage);
        TabPane imageTabPane = new TabPane();
        Tab imageTab = new Tab("Test Topology");
        imageTab.setContent(topo);
        imageTabPane.getTabs().add(imageTab);
        imageTabPane.setMinWidth(300);
        rightPane.getItems().addAll(imageTabPane, consoleTabPane);
        rightPane.setDividerPosition(1, 400);
        baseSplitPane.setDividerPosition(1, 10);
        baseSplitPane.getItems().addAll(leftPane, rightPane);
        return baseSplitPane;
    }

    public void getDebugTab() {
        poxSessionText.prefWidth(450);
        poxSessionText.prefHeight(620);
        poxSessionText.setStyle(
                "-fx-text-fill: #0A0A2A;"
                + "-fx-background-color: #EFFBFB;");
        poxSessionText.setEditable(false);
        poxSessionTab.setContent(poxSessionText);
        flowVisorSessionText.prefWidth(450);
        flowVisorSessionText.prefHeight(620);
        flowVisorSessionText.setStyle(
                "-fx-text-fill: #0A0A2A;"
                + "-fx-background-color: #EFFBFB;");
        flowVisorSessionText.setEditable(false);
        dpctlSessionTab.setContent(flowVisorSessionText);
        mininetSessionText.prefWidth(450);
        mininetSessionText.prefHeight(620);
        mininetSessionText.setStyle(
                "-fx-text-fill: #0A0A2A;"
                + "-fx-background-color: #EFFBFB;");
        mininetSessionText.setEditable(false);
        mininetSessionTab.setContent(mininetSessionText);
        debugLogText.prefWidth(450);
        debugLogText.prefHeight(620);
        debugLogText.setStyle(
                "-fx-text-fill: #0A0A2A;"
                + "-fx-background-color: #EFFBFB;");
        debugLogText.setEditable(false);
        componentLog.setClosable(false);
        compononetLogText.prefWidth(350);
        compononetLogText.prefHeight(620);
        compononetLogText.setStyle(
                "-fx-text-fill: #0A0A2A;"
                + "-fx-background-color: #EFFBFB;");
        compononetLogText.setEditable(false);
        componentLog.setContent(compononetLogText);
        debugLog.setClosable(false);
        debugLog.setContent(debugLogText);
        debugLog.setContent(debugLogText);
    }

    public void getToolBar() {
        Image pauseImage = new Image("images/Pause.png", 20.0, 20.0, true, true);
        Button pause = new Button("", new ImageView(pauseImage));
        Image stopImage = new Image("images/Stop.png", 20.0, 20.0, true, true);
        Button stop = new Button("", new ImageView(stopImage));
        stop.setTooltip(new Tooltip("Stop"));

        Image resumeImage = new Image("images/Resume_1.png", 20.0, 20.0, true, true);
        Button resume = new Button("", new ImageView(resumeImage));
        resume.setTooltip(new Tooltip("Resume"));

        Image dumpVarImage = new Image("images/dumpvar.png", 20.0, 20.0, true, true);
        Button dumpVar = new Button("", new ImageView(dumpVarImage));
        dumpVar.setTooltip(new Tooltip("Dump Var"));

        Image showlogImage = new Image("images/showlog.jpg", 20.0, 20.0, true, true);
        Button showlog = new Button("", new ImageView(showlogImage));
        showlog.setTooltip(new Tooltip("Show Log"));

        Image currentCaseImage = new Image("images/currentcase.jpg", 20.0, 20.0, true, true);
        Button currentcase = new Button("", new ImageView(currentCaseImage));
        currentcase.setTooltip(new Tooltip("Current Case"));

        Image currentStepImage = new Image("images/currentstep.png", 20.0, 20.0, true, true);
        Button currentStep = new Button("", new ImageView(currentStepImage));
        currentStep.setTooltip(new Tooltip("Current Step"));

        Image nextStepImage = new Image("images/nextStep.jpg", 20.0, 20.0, true, true);
        Button nextStep = new Button("", new ImageView(nextStepImage));
        nextStep.setTooltip(new Tooltip("Next Step"));

        Image compileImage = new Image("images/compile.jpg", 20.0, 20.0, true, true);
        Button compile = new Button("", new ImageView(compileImage));
        compile.setTooltip(new Tooltip("Compile"));

        Image getTestImage = new Image("images/testname.jpg", 20.0, 20.0, true, true);
        Button getTest = new Button("", new ImageView(getTestImage));
        getTest.setTooltip(new Tooltip("Get Test"));

        Image interpretImage = new Image("images/interpreter.jpg", 20.0, 20.0, true, true);
        Button interpret = new Button("", new ImageView(interpretImage));
        interpret.setTooltip(new Tooltip("Interpret"));

        Image doImage = new Image("images/do.jpg", 20.0, 20.0, true, true);
        Button doCommand = new Button("", new ImageView(doImage));
        doCommand.setTooltip(new Tooltip("Do"));

        Image redoImage = new Image("images/redo.png", 20.0, 20.0, true, true);
        Button redoCommand = new Button("", new ImageView(redoImage));
        redoCommand.setTooltip(new Tooltip("Re-execute"));

        final Button submit = new Button("Enter");
        final TextField value = TextFieldBuilder.create().build();
        value.setMinWidth(480);
        final ExecutionConsole execConsole = new ExecutionConsole(command, submit, value);

        redoCommand.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent t) {
                requestServer("redo", new Vector());
                requestServer("resume", new Vector());
            }
        });

        getTest.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent t) {
                requestServer("getTest", new Vector());
            }
        });

        doCommand.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent t) {
                try {
                    command = "doCommand";
                    execConsole.start(new Stage());
                    execConsole.setTitles("do Command");
                } catch (Exception ex) {
                    Logger.getLogger(OFATestSummary.class.getName()).log(Level.SEVERE, null, ex);
                }
            }
        });

        interpret.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent t) {
                try {
                    value.setEditable(true);
                    command = "interpret";
                    execConsole.start(new Stage());
                    execConsole.setTitles("interpret Command");
                } catch (Exception ex) {
                    Logger.getLogger(OFATestSummary.class.getName()).log(Level.SEVERE, null, ex);
                }
            }
        });

        compile.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent t) {
                try {
                    command = "doCompile";
                    execConsole.start(new Stage());
                    execConsole.setTitles("compile Command");
                } catch (Exception ex) {
                    Logger.getLogger(OFATestSummary.class.getName()).log(Level.SEVERE, null, ex);
                }
            }
        });

        resume.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent t) {
                requestServer("resume", new Vector());
            }
        });

        nextStep.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent t) {
                requestServer("nextStep", new Vector());
            }
        });

        currentStep.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent t) {
                requestServer("currentStep", new Vector());
            }
        });

        currentcase.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent t) {
                requestServer("currentCase", new Vector());
            }
        });

        showlog.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent t) {
                requestServer("showLog", new Vector());
            }
        });

        submit.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent t) {
                variableName = value.getText();
                execConsole.closeWindow();
                Vector params = new Vector();
                params.add(variableName);
                requestServer(command, params);
            }
        });
        dumpVar.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent t) {
                try {
                    command = "dumpVar";
                    execConsole.start(new Stage());
                    execConsole.setTitles("dumpvar Command");
                } catch (Exception ex) {
                    Logger.getLogger(OFATestSummary.class.getName()).log(Level.SEVERE, null, ex);
                }


            }
        });

        pause.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent t) {
                XmlRpcClient server;
                try {
                    server = new XmlRpcClient("http://localhost:9000");
                    try {
                        Object response = server.execute("pauseTest", new Vector());
                        compononetLogText.appendText("\n Will pause the test's execution, after completion of this step.....\n\n");
                    } catch (XmlRpcException ex) {
                        Logger.getLogger(OFATestSummary.class.getName()).log(Level.SEVERE, null, ex);
                    } catch (IOException ex) {
                        Logger.getLogger(OFATestSummary.class.getName()).log(Level.SEVERE, null, ex);
                    }
                } catch (MalformedURLException ex) {
                    Logger.getLogger(OFATestSummary.class.getName()).log(Level.SEVERE, null, ex);
                }
            }
        });

        stop.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent t) {
                XmlRpcClient server;
                try {
                    server = new XmlRpcClient("http://localhost:9000");
                    Vector params = new Vector();
                    try {
                        server.execute("stop", new Vector());
                    } catch (XmlRpcException ex) {
                        Logger.getLogger(OFATestSummary.class.getName()).log(Level.SEVERE, null, ex);
                    } catch (IOException ex) {
                        Logger.getLogger(OFATestSummary.class.getName()).log(Level.SEVERE, null, ex);
                    }
                } catch (MalformedURLException ex) {
                    Logger.getLogger(OFATestSummary.class.getName()).log(Level.SEVERE, null, ex);
                }
            }
        });

        quickLauchBar.getItems().addAll(pause, resume, stop, new Separator(Orientation.VERTICAL), dumpVar, currentcase, currentStep, showlog, nextStep,
                new Separator(Orientation.VERTICAL), getTest, compile, doCommand, interpret, redoCommand);
    }

    public void requestServer(String request, Vector params) {

        XmlRpcClient server;
        try {
            server = new XmlRpcClient("http://localhost:9000");
            try {
                Object response = server.execute(request, params);
                javafx.scene.control.SingleSelectionModel<Tab> selectionModel = consoleTabPane.getSelectionModel();
                selectionModel.select(debugLog);
                debugLogText.appendText(request + " Ouput \n =====================================================================\n");
                debugLogText.appendText(response.toString());
                debugLogText.appendText("\n ======================================================================\n");
            } catch (XmlRpcException ex) {
                Logger.getLogger(OFATestSummary.class.getName()).log(Level.SEVERE, null, ex);
            } catch (IOException ex) {
                Logger.getLogger(OFATestSummary.class.getName()).log(Level.SEVERE, null, ex);
            }
        } catch (MalformedURLException ex) {
            Logger.getLogger(OFATestSummary.class.getName()).log(Level.SEVERE, null, ex);
        }
    }

    public Button getVieLogsButton() {
        return viewLogs;
    }

    public StackPane getRoot() {
        return rootStack;
    }

    public ObservableList<SummaryTable> getData() {
        return data;
    }

    public PieChart getChart() {
        return chart;
    }

    public TableView getFinalSummaryTable() {
        return finalSummaryTable;
    }

    public ObservableList<FinalSummaryTable> getFinalSummaryData() {
        return summaryData;
    }

    public ObservableList<PieChart.Data> getpieChartData() {
        return pieChartData;
    }

    public javafx.scene.control.TextArea getTextArea(String name) {
        if (name.equals("log")) {
            return compononetLogText;
        } else if (name.equals("pox")) {
            return poxSessionText;
        } else if (name.equals("flowvisor")) {
            return flowVisorSessionText;
        } else if (name.equals("mininet")) {
            return mininetSessionText;
        }
        return new javafx.scene.control.TextArea();
    }

    public PieChart.Data getPassData() {
        return passData;
    }

    public PieChart.Data getFailData() {
        return failData;
    }

    public PieChart.Data getAbortData() {
        return abortData;
    }

    public PieChart.Data getNoResultData() {
        return noResult;
    }

    ///Step TABLE 
    public TableView getStepTable() {
        return stepTable;
    }

    public ObservableList<StepTable> getStepData() {
        return stepData;
    }
}
