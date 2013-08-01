/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package tai_ofa;

import java.util.Iterator;
import javafx.application.Application;
import javafx.application.Platform;
import javafx.collections.ObservableList;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.geometry.Insets;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.CheckBox;
import javafx.scene.control.ComboBox;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import javafx.scene.control.TreeItem;
import javafx.scene.control.TreeView;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.StackPane;
import javafx.stage.Stage;

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
public class OFATestParameters extends Application {

    Stage stage;
    TAI_OFA ofaReferernce;
    TreeView<String> projectExplorerTreeView;
    OFATestSummary testSummaryPop;
    TreeItem<String> selectetdTest;
    ObservableList<TreeItem<String>> listProject;
    ObservableList<TreeItem<String>> paramFile;
    ComboBox<String> paramList;
    ComboBox<String> topologyList;
    String projectToRun;
    /**
     * @param args the command line arguments
     */
    Button selectTestCase = new Button("Select TestCases");
    Button startTest = new Button("Start Test");
    Button cancelButton = new Button("Cancel");

    public void setProjectView(TreeView<String> tree) {
        projectExplorerTreeView = tree;
    }

    public OFATestParameters(TAI_OFA ofaReference) {
        this.ofaReferernce = ofaReference;
    }

    public void setProjectList(ObservableList<TreeItem<String>> list) {
        listProject = list;
    }

    public static void main(String[] args) {
        launch(args);
    }

    @Override
    public void start(Stage primaryStage) {
        testSummaryPop = new OFATestSummary(ofaReferernce, stage);
        stage = primaryStage;
        primaryStage.setTitle("Test ParaMeter");
        primaryStage.setResizable(false);
        GridPane testParameterGrid = new GridPane();
        testParameterGrid.setPadding(new Insets(100, 0, 0, 60));
        testParameterGrid.setVgap(8);
        testParameterGrid.setHgap(2);

        selectTestCase.setDisable(true);
        startTest.setDisable(true);
        Label projectName = new Label("Test Name :");;
        testParameterGrid.add(projectName, 0, 1);
        final ComboBox<String> projectNameList = new ComboBox<String>();
        projectNameList.setMinWidth(170);

        ObservableList<String> dataForProject = projectNameList.getItems();
        final Iterator<TreeItem<String>> projectIterator = listProject.iterator();
        while (projectIterator.hasNext()) {
            final TreeItem<String> treeItem = projectIterator.next();
            dataForProject.add(treeItem.getValue());
            ObservableList<TreeItem<String>> list = treeItem.getChildren();
            Iterator<TreeItem<String>> it = list.iterator();
        }
        projectNameList.setItems(dataForProject);
        testParameterGrid.add(projectNameList, 1, 1);
        projectNameList.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent arg0) {
                final Iterator<TreeItem<String>> projectIterator = listProject.iterator();
                while (projectIterator.hasNext()) {
                    final TreeItem<String> treeItem = projectIterator.next();
                    ObservableList<TreeItem<String>> list = treeItem.getChildren();
                    if (treeItem.getValue().equalsIgnoreCase(projectNameList.getSelectionModel().getSelectedItem())) {
                        ObservableList<TreeItem<String>> children = treeItem.getChildren();
                        final Iterator<TreeItem<String>> testListIterator = children.iterator();
                        while (testListIterator.hasNext()) {
                            selectetdTest = testListIterator.next();
                            paramFile = selectetdTest.getChildren();
                            if (selectetdTest.getGraphic().getId().equals(".params")) {
                                paramList.getItems().add(selectetdTest.getValue());
                            }

                            if (selectetdTest.getGraphic().getId().equals(".topo")) {
                                topologyList.getItems().add(selectetdTest.getValue());
                            }
                            selectTestCase.setDisable(false);
                            startTest.setDisable(false);
                        }
                    }
                }
            }
        });

        Label params = new Label("Params");
        testParameterGrid.add(params, 0, 3);
        paramList = new ComboBox<String>();
        paramList.setMinWidth(170);
        testParameterGrid.add(paramList, 1, 3);

        Label topology = new Label("Topology");
        testParameterGrid.add(topology, 0, 4);
        topologyList = new ComboBox<String>();
        topologyList.setMinWidth(170);
        testParameterGrid.add(topologyList, 1, 4);

        Label logFolder = new Label("Log Folder");
        testParameterGrid.add(logFolder, 0, 5);
        TextField logFolderPath = new TextField();
        logFolderPath.setMaxWidth(170);
        testParameterGrid.add(logFolderPath, 1, 5);
        Label cliOption = new Label("CLI Options:");
        testParameterGrid.add(cliOption, 0, 6);

        HBox testDirBox = new HBox(5);
        CheckBox testDirCheck = new CheckBox("Test Directory");
        TextField testDirPath = new TextField();
        testDirPath.setMaxWidth(140);
        testDirBox.getChildren().addAll(testDirCheck, testDirPath);
        testParameterGrid.add(testDirBox, 1, 7);

        HBox emailBox = new HBox(5);
        CheckBox emailIdCheck = new CheckBox("Email Id          ");
        TextField emailText = new TextField();
        emailText.setMaxWidth(140);
        emailBox.getChildren().addAll(emailIdCheck, emailText);
        testParameterGrid.add(emailBox, 1, 8);

        HBox optionButton = new HBox(5);
        optionButton.setPadding(new Insets(0, 0, 0, 0));
        optionButton.getChildren().addAll(selectTestCase, startTest, cancelButton);
        testParameterGrid.add(optionButton, 1, 11);

        selectTestCase.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent arg0) {
                String testName = projectNameList.getSelectionModel().getSelectedItem();
                String paramsFileName = paramList.getSelectionModel().getSelectedItem();
                OFATestCaseSelection testCasePop = new OFATestCaseSelection(testName, paramsFileName);
                testCasePop.start(new Stage());
            }
        });

        startTest.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent arg0) {
                testSummaryPop.start(new Stage());
                Runnable firstRunnable = new Runnable() {
                    public void run() {
                        try {
                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                    }
                };

                Runnable secondRunnable = new Runnable() {
                    public void run() {
                        try {
                            ExecuteTest tail = new ExecuteTest(testSummaryPop.getTable(), testSummaryPop.getData(), testSummaryPop.getChart(),
                                    testSummaryPop.getFinalSummaryTable(), testSummaryPop.getFinalSummaryData(),
                                    testSummaryPop.getVieLogsButton(), testSummaryPop.getpieChartData(),
                                    testSummaryPop.getPassData(), testSummaryPop.getFailData(), testSummaryPop.getAbortData(),
                                    testSummaryPop.getNoResultData(), projectNameList.getSelectionModel().getSelectedItem().toString(), testSummaryPop.getTextArea("log"), testSummaryPop.getStepTable(), testSummaryPop.getStepData(), testSummaryPop.getTextArea("pox"), testSummaryPop.getTextArea("mininet"), testSummaryPop.getTextArea("flowvisor"));
                            tail.runTest();
                        } catch (Exception iex) {
                        }
                    }
                };
                Platform.runLater(firstRunnable);
                Platform.runLater(secondRunnable);
                stage.close();
            }
        });
        StackPane root = new StackPane();
        root.getChildren().add(testParameterGrid);
        primaryStage.setScene(new Scene(root, 460, 360));
        primaryStage.show();
    }
}
