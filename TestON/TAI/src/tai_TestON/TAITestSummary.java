/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package tai_TestON;

/**
*
* @author Raghavkashyap (raghavkashyap@paxterra.com)

* TestON is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 2 of the License, or
* (at your option) any later version.

* TestON is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
* GNU General Public License for more details.

* You should have received a copy of the GNU General Public License
* along with TestON. If not, see <http://www.gnu.org/licenses/>.

*/


import java.io.IOException;
import java.net.MalformedURLException;
import java.sql.Timestamp;
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
import javafx.scene.control.RadioButton;
import javafx.scene.control.Separator;
import javafx.scene.control.SplitPane;
import javafx.scene.control.Tab;
import javafx.scene.control.TabPane;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableView;
import javafx.scene.control.TextAreaBuilder;
import javafx.scene.control.TextField;
import javafx.scene.control.TextFieldBuilder;
import javafx.scene.control.TitledPane;
import javafx.scene.control.Toggle;
import javafx.scene.control.ToggleGroup;
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
import javax.xml.bind.ValidationEvent;
import org.apache.xmlrpc.XmlRpcClient;
import org.apache.xmlrpc.XmlRpcException;

/**
 *
 * @author Raghav Kashyap (raghavkashyap@paxterrasolutions.com)
 */
public class TAITestSummary extends Application {

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
    
    GridPane buttonPane = new GridPane();
    TableColumn stepId, stepName, stepStatus;
    TableColumn summaryItem, information;
    HashMap<String, String> testCaseIdAndName = new HashMap<String, String>();
    String caseId, caseName;
    Stage copyStage;
    PieChart chart;
    StackPane rootStack;
    TAI_TestON ofaReference;
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
    
    String variableName = "";
    String command = "";
    ToolBar quickLauchBar = new ToolBar();
    Double toolBarHeight;
    Scene scene;
    SplitPane baseSplitPane = new SplitPane();
    TabPane consoleTabPane;
    TextField currentTest = new TextField();
    TextField currentStep = new TextField();
    TextField currentCase  = new TextField();
    HashMap<String, String> addedContent = new HashMap<>();

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        launch(args);
    }

    public TAITestSummary(TAI_TestON ofaReference, Stage paramaterWindow) {
        this.ofaReference = ofaReference;
        this.paramaterWindow = paramaterWindow;
    }

    public void start(Stage primaryStage) {
        copyStage = primaryStage;
        primaryStage.setTitle("Test Execution Status");
        //primaryStage.setResizable(false);
        Group rootGroup = new Group();
        scene = new Scene(rootGroup, 1020, 920);
        Pane basePanel = new Pane();
        HBox baseBox = new HBox();
        VBox consoleBox = new VBox();
        VBox buttonBox = new VBox();

        componentLog.setClosable(false);
        compononetLogText.prefWidth(350);
        compononetLogText.prefHeight(620);
        compononetLogText.setStyle(
                "-fx-text-fill: #0A0A2A;"
                + "-fx-background-color: #EFFBFB;");
        compononetLogText.setEditable(false);
        componentLog.setContent(compononetLogText);
        
        
        getDebugTab();
        getToolBar();
        buttonBox.getChildren().addAll(buttonPane);
        consoleBox.getChildren().addAll(quickLauchBar, baseTabPane);
        baseBox.getChildren().addAll(consoleBox);
        basePanel.getChildren().addAll(baseBox);
        SplitPane sp = getTestSummary();
        testSummaryTab.setContent(sp);
        testSummaryTab.setClosable(false);
        baseTabPane.getTabs().addAll(testSummaryTab,debugLog);
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
                        Logger.getLogger(TAITestSummary.class.getName()).log(Level.SEVERE, null, ex);
                    } catch (IOException ex) {
                        Logger.getLogger(TAITestSummary.class.getName()).log(Level.SEVERE, null, ex);
                    }
                } catch (MalformedURLException ex) {
                    Logger.getLogger(TAITestSummary.class.getName()).log(Level.SEVERE, null, ex);
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
        consoleTabPane.getTabs().addAll(componentLog);

        Image topoImage = new Image("images/topo.png", 400, 200, true, true);
        ImageView topo = new ImageView(topoImage);
        TabPane imageTabPane = new TabPane();
        Tab imageTab = new Tab("Test Topology");
        imageTab.setContent(topo);
        imageTabPane.getTabs().add(imageTab);
        imageTabPane.setMinWidth(300);
        rightPane.getItems().addAll(consoleTabPane);
        rightPane.setDividerPosition(1, 400);
        baseSplitPane.setDividerPosition(1, 10);
        baseSplitPane.getItems().addAll(leftPane, rightPane);
        return baseSplitPane;
    }

    public void getDebugTab() {
  
        GridPane debugGrid = new GridPane();
        debugGrid.setPadding(new Insets(15, 15, 0, 10));
        
        
        VBox staticUpdate  = new VBox();
        VBox dynamicUpdate = new VBox();
        
        Label caseLable = new Label("Current Case :");
        Label stepLable = new Label("Current Step :");
        Label testLable = new Label("Current Test :");
        
        
        final javafx.scene.control.TextArea historyText = TextAreaBuilder.create().build();
        Label commandHistory = new Label("History");
        
                 
        GridPane dynamiGridPane = new GridPane();
        dynamiGridPane.setPadding(new Insets(15, 15, 0, 10));
        dynamiGridPane.setHgap(20);
        dynamiGridPane.setVgap(10);

        GridPane staticGridPane = new GridPane();
        staticGridPane.setPadding(new Insets(15, 15, 0, 10));
        staticGridPane.setHgap(10);
        staticGridPane.setVgap(10);  
        
        dynamiGridPane.add(testLable, 0, 0);
        dynamiGridPane.add(currentTest, 1, 0);
        dynamiGridPane.add(stepLable, 2, 0);
        dynamiGridPane.add(currentStep, 3, 0);
        dynamiGridPane.add(caseLable, 4, 0);
        dynamiGridPane.add(currentCase, 5, 0);
        
        Button nextStep = new Button("<< Next Step >>");
        staticGridPane.add(nextStep, 0, 0);
        
        nextStep.setOnAction(new EventHandler<ActionEvent>() {

            @Override
            public void handle(ActionEvent t) {
                 requestServer("nextStep", new Vector());
            }
        });
         
        Label doCommand = new Label("Run OSPK Command :"); 
        final TextField doCommandText = new TextField();
        Button runDoCommand = new Button("Run");
        final CheckBox addingStep = new CheckBox("Add After Current Step");
        addingStep.setSelected(true);
        
        doCommandText.setMinWidth(600);
        ToggleGroup pythonOrOspk = new ToggleGroup();
        final RadioButton pythonRadio = new RadioButton("py");
        RadioButton ospkRadio = new RadioButton("OSPK");
        pythonOrOspk.getToggles().addAll(pythonRadio,ospkRadio);
        
        runDoCommand.setOnAction(new EventHandler<ActionEvent>() {

            @Override
            public void handle(ActionEvent t) {
                  if (pythonRadio.isSelected()){
                      Object output = requestServer("py", doCommandText.getText());    
                      doCommandText.clear();
                  }else {
                      Object output = requestServer("doCommand", doCommandText.getText());
                      java.util.Date date= new java.util.Date();
                      String historyCommand = "\n" + new Timestamp(date.getTime()).toString() + "---" + currentStep.getText().toString() +"---"+" do " + doCommandText.getText();
                      historyText.appendText(historyCommand); 
                      
                      if(addingStep.isSelected()){
                          addedContent.put(currentStep.getText().toString(), doCommandText.getText().toString());
                      }
                      doCommandText.clear();
                  }
                  
                  
                  
            }
        });
        
        HBox radioBox = new HBox(10);
        radioBox.getChildren().addAll(pythonRadio,ospkRadio,addingStep);
        staticGridPane.add(doCommand, 0, 1);
        staticGridPane.add(doCommandText, 1, 1);
        staticGridPane.add(runDoCommand, 2, 1);
        staticGridPane.add(radioBox, 1, 2);
        //staticGridPane.add(addingStep, 2, 2);
      
        
        
        
        Label dumpVar = new Label("Dump Variable :");
        final TextField dumpVarText = new TextField();
        Button dumpVarButton  =  new Button("Dump");
        Label dumpVarOutput = new Label("Output :");
        final javafx.scene.control.TextArea dumpVarOutText = TextAreaBuilder.create().build();
        
        staticGridPane.add(dumpVar, 0, 4);
        staticGridPane.add(dumpVarText, 1, 4);
        staticGridPane.add(dumpVarButton, 2, 4);
        staticGridPane.add(dumpVarOutput, 0, 5);
        staticGridPane.add(dumpVarOutText, 1, 5);
        
        dumpVarButton.setOnAction(new EventHandler<ActionEvent>() {

            @Override
            public void handle(ActionEvent t) {
                Object output = requestServer("dumpVar", dumpVarText.getText());
                dumpVarOutText.setText(output.toString());
                java.util.Date date= new java.util.Date();
                      String historyCommand = "\n" + new Timestamp(date.getTime()).toString() + "---" + currentStep.getText().toString() +"---"+" dumpVar " + dumpVarText.getText();
                     historyText.appendText(historyCommand); 
                
            }
        });
        
        
        Label interpret = new Label("Interpret :");
        final TextField interpretText = new TextField();
        Button interpretButton  =  new Button("Run");
        Label interpretOutput = new Label("Output :");
        final javafx.scene.control.TextArea interpretOutText = TextAreaBuilder.create().build();
        
        interpretButton.setOnAction(new EventHandler<ActionEvent>() {

            @Override
            public void handle(ActionEvent t) {
                Object output = requestServer("interpret", interpretText.getText());
                interpretOutText.setText(output.toString());
                java.util.Date date= new java.util.Date();
                      String historyCommand = "\n" + new Timestamp(date.getTime()).toString() + "---" + currentStep.getText().toString() +"---"+ " interpret " + interpretText.getText();
                     historyText.appendText(historyCommand); 
            }
        });
        
        staticGridPane.add(interpret, 0, 9);
        staticGridPane.add(interpretText, 1, 9);
        staticGridPane.add(interpretButton, 2, 9);
        staticGridPane.add(interpretOutput, 0, 10);
        staticGridPane.add(interpretOutText, 1, 10);
        
        dynamicUpdate.getChildren().addAll(dynamiGridPane);
        staticUpdate.getChildren().addAll(staticGridPane);
        
        
        staticGridPane.add(commandHistory, 0, 13);
        staticGridPane.add(historyText, 1, 13);
        
        VBox finalBox = new VBox();
        finalBox.getChildren().addAll(dynamicUpdate,staticUpdate);
        debugGrid.getChildren().addAll(finalBox);
        debugLog.setClosable(false);
        debugLog.setContent(debugGrid);
        
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

       
        resume.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent t) {
                requestServer("resume", new Vector());
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
                        Logger.getLogger(TAITestSummary.class.getName()).log(Level.SEVERE, null, ex);
                    } catch (IOException ex) {
                        Logger.getLogger(TAITestSummary.class.getName()).log(Level.SEVERE, null, ex);
                    }
                } catch (MalformedURLException ex) {
                    Logger.getLogger(TAITestSummary.class.getName()).log(Level.SEVERE, null, ex);
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
                        Logger.getLogger(TAITestSummary.class.getName()).log(Level.SEVERE, null, ex);
                    } catch (IOException ex) {
                        Logger.getLogger(TAITestSummary.class.getName()).log(Level.SEVERE, null, ex);
                    }
                } catch (MalformedURLException ex) {
                    Logger.getLogger(TAITestSummary.class.getName()).log(Level.SEVERE, null, ex);
                }
            }
        });

        quickLauchBar.getItems().addAll(pause, resume, stop );
    }

    public Object requestServer(String request, String parameters) {

        XmlRpcClient server;
        Object response = null;
        Vector params = new Vector();
        params.add(parameters);
        try {
            server = new XmlRpcClient("http://localhost:9000");
            try {
                response = server.execute(request, params);
                
            } catch (XmlRpcException ex) {
                Logger.getLogger(TAITestSummary.class.getName()).log(Level.SEVERE, null, ex);
            } catch (IOException ex) {
                Logger.getLogger(TAITestSummary.class.getName()).log(Level.SEVERE, null, ex);
            }
        } catch (MalformedURLException ex) {
            Logger.getLogger(TAITestSummary.class.getName()).log(Level.SEVERE, null, ex);
        }
        
        return  response;
    }
    
    
    public void requestServer(String request, Vector params) {

        XmlRpcClient server;
        try {
            server = new XmlRpcClient("http://localhost:9000");
            try {
                Object response = server.execute(request, params);
                
            } catch (XmlRpcException ex) {
                Logger.getLogger(TAITestSummary.class.getName()).log(Level.SEVERE, null, ex);
            } catch (IOException ex) {
                Logger.getLogger(TAITestSummary.class.getName()).log(Level.SEVERE, null, ex);
            }
        } catch (MalformedURLException ex) {
            Logger.getLogger(TAITestSummary.class.getName()).log(Level.SEVERE, null, ex);
        }
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
