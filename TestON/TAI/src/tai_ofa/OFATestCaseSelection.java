/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package tai_ofa;

import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.Locale;
import java.util.Map;
import java.util.TreeMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javafx.application.Application;
import javafx.beans.value.ChangeListener;
import javafx.beans.value.ObservableValue;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.geometry.Insets;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.CheckBox;
import javafx.scene.control.Label;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableView;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.scene.image.ImageView;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.StackPane;
import javafx.scene.text.Text;
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
public class OFATestCaseSelection extends Application {

    String driverFile;
    String paramFileName;
    String pythonFile;
    TAILocale label = new TAILocale(Locale.ENGLISH);

    OFATestCaseSelection(String fileName, String paramsFileName) {
        driverFile = label.hierarchyTestON + "/tests/" + fileName + "/" + fileName + ".ospk";
        pythonFile = label.hierarchyTestON + "/tests/" + fileName + "/" + fileName + ".py";
        paramFileName = label.hierarchyTestON + "/tests/" + fileName + "/" + fileName + ".params";
    }
    ObservableList<TestCaseSelectionTable> data;
    ObservableList<String> testSelected;
    TableView<TestCaseSelectionTable> deviceTable;
    TableColumn selectCaseColumn;
    TableColumn testCaseIdColumn;
    TableColumn testCaseNameColumn;
    TreeMap<String, String> testCaseIdAndName = new TreeMap<String, String>();
    String caseId, caseName;
    GridPane testCaseSelectionGrid = new GridPane();
    TreeMap<String, String> stepHash = new TreeMap<String, String>();
    TableColumn stepId, stepName;
    TableView<TestSelectStepTable> stepTable;
    ObservableList<TestSelectStepTable> stepData;

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        launch(args);
    }

    @Override
    public void start(final Stage primaryStage) {
        primaryStage.setTitle("TestCase Selection");
        primaryStage.setResizable(false);
        testSelected = FXCollections.observableArrayList();
        stepData = FXCollections.observableArrayList();

        testCaseSelectionGrid.setPadding(new Insets(0, 0, 0, 15));
        testCaseSelectionGrid.setVgap(10);
        testCaseSelectionGrid.setHgap(20);
        final CheckBox selectTestCase = new CheckBox();
        Label testCaseId = new Label("");
        Label testCaseName = new Label("");

        stepTable = new TableView<TestSelectStepTable>();
        deviceTable = new TableView<TestCaseSelectionTable>();
        data = FXCollections.observableArrayList(new TestCaseSelectionTable(selectTestCase, testCaseId, testCaseName));
        deviceTable.setMinWidth(430);
        deviceTable.setMaxHeight(300);
        testCaseIdColumn = new TableColumn();

        testCaseIdColumn.setCellValueFactory(new PropertyValueFactory<TestCaseSelectionTable, CheckBox>("testCaseCheckBox"));
        testCaseIdColumn.setMinWidth(90);
        testCaseIdColumn.setResizable(false);
        selectCaseColumn = new TableColumn("TestCase Id");
        selectCaseColumn.setSortable(true);
        selectCaseColumn.setCellValueFactory(new PropertyValueFactory<TestCaseSelectionTable, Label>("testCaseId"));
        selectCaseColumn.setMinWidth(130);
        selectCaseColumn.setResizable(false);
        testCaseNameColumn = new TableColumn("TestCase Name");
        testCaseNameColumn.setCellValueFactory(new PropertyValueFactory<TestCaseSelectionTable, Label>("testCaseName"));
        testCaseNameColumn.setMinWidth(130);
        testCaseNameColumn.setResizable(false);
        deviceTable.setItems(data);
        deviceTable.getColumns().addAll(testCaseIdColumn, selectCaseColumn, testCaseNameColumn);
        stepTable.setMinWidth(620);
        stepTable.setMaxHeight(330);

        stepId = new TableColumn("ID");
        stepId.setCellValueFactory(new PropertyValueFactory<TestSelectStepTable, Label>("testStepId"));
        stepId.setMinWidth(10);
        stepId.setResizable(true);

        stepName = new TableColumn("Name");
        stepName.setCellValueFactory(new PropertyValueFactory<TestSelectStepTable, Label>("testStepName"));
        stepName.setMinWidth(400);
        stepName.setResizable(true);


        stepTable.getColumns().addAll(stepId, stepName);
        stepTable.setItems(stepData);
        driverFunctionName();

        Iterator driverFileIterator = testCaseIdAndName.entrySet().iterator();
        while (driverFileIterator.hasNext()) {
            Map.Entry testCaseDetail = (Map.Entry) driverFileIterator.next();
            final CheckBox selectcase = new CheckBox();
            final Label id = new Label((String) testCaseDetail.getKey());
            Label name = new Label((String) testCaseDetail.getValue());
            selectTestCase.selectedProperty().addListener(new ChangeListener<Boolean>() {
                @Override
                public void changed(ObservableValue<? extends Boolean> arg0, Boolean arg1, Boolean arg2) {
                    selectcase.setSelected(true);
                    if (selectTestCase.isSelected() == false) {
                        selectcase.setSelected(false);
                    }
                }
            });

            selectcase.selectedProperty().addListener(new ChangeListener<Boolean>() {
                @Override
                public void changed(ObservableValue<? extends Boolean> arg0, Boolean arg1, Boolean arg2) {
                    if (selectcase.isSelected() == true) {
                        stepData.clear();
                        for (int i = 0; i < deviceTable.getItems().size(); i++) {
                            if (deviceTable.getItems().get(i).testCaseId.getText().equals(id.getText())) {
                                deviceTable.getSelectionModel().select(i);
                                Pattern caseNumberPattern = Pattern.compile("CASE\\s*(\\d+)");
                                Matcher caseNumberMatcher = caseNumberPattern.matcher(deviceTable.getItems().get(i).testCaseId.getText());
                                String caseNumber = "";
                                if (caseNumberMatcher.find()) {
                                    caseNumber = caseNumberMatcher.group(1);
                                }

                                getTestSteps(caseNumber);
                                testSelected.add(caseNumber);

                                Iterator entries = stepHash.entrySet().iterator();
                                while (entries.hasNext()) {
                                    Map.Entry entry = (Map.Entry) entries.next();
                                    String key = (String) entry.getKey();
                                    String value = (String) entry.getValue();
                                    stepData.add(new TestSelectStepTable(new Label(key), new Label(value)));
                                }

                                stepTable.setItems(stepData);
                                stepTable.setVisible(true);
                                try {
                                    testCaseSelectionGrid.add(new Text("Test Steps :"), 0, 3);
                                    testCaseSelectionGrid.add(stepTable, 0, 4);
                                } catch (Exception e) {
                                }
                            }
                        }
                    }

                    if (deviceTable.getSelectionModel().getSelectedItem().getTestCaseCheckBox().isSelected() == true) {
                    }
                }
            });

            data.add(new TestCaseSelectionTable(selectcase, id, name));
            testCaseIdColumn.setCellValueFactory(new PropertyValueFactory<TestCaseSelectionTable, CheckBox>("testCaseCheckBox"));
            testCaseIdColumn.setMinWidth(50);
            testCaseIdColumn.setResizable(false);

            selectCaseColumn.setCellValueFactory(new PropertyValueFactory<TestCaseSelectionTable, Label>("testCaseId"));
            selectCaseColumn.setMinWidth(100);
            selectCaseColumn.setResizable(false);

            testCaseNameColumn.setCellValueFactory(new PropertyValueFactory<TestCaseSelectionTable, Label>("testCaseName"));
            testCaseNameColumn.setMinWidth(292);
            testCaseNameColumn.setResizable(false);
            deviceTable.setItems(data);
        }

        testCaseSelectionGrid.add(deviceTable, 0, 1);

        HBox optionButton = new HBox(5);
        optionButton.setPadding(new Insets(0, 0, 0, 0));

        Button startTest = new Button("Save");

        startTest.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent t) {
                for (int i = 0; i < deviceTable.getItems().size(); i++) {

                    if (deviceTable.getItems().get(i).testCaseIdCheck.isSelected()) {
                        deviceTable.getSelectionModel().select(i);
                    }

                    if (deviceTable.getSelectionModel().getSelectedItem().getTestCaseCheckBox().isSelected() == true) {
                    }
                }

                StringBuilder testcases = new StringBuilder();
                for (String s : testSelected) {
                    testcases.append(s).append(',');
                }
                primaryStage.close();
            }
        });

        Button modifyParams = new Button("Modify Params");
        Button cancelButton = new Button("Cancel");
        optionButton.getChildren().addAll(new Label("                                    "), startTest, modifyParams, cancelButton);
        testCaseSelectionGrid.add(optionButton, 0, 5);

        StackPane root = new StackPane();
        root.getChildren().add(testCaseSelectionGrid);
        primaryStage.setScene(new Scene(root, 650, 400));
        primaryStage.show();
    }

    public void driverFunctionName() {
        try {
            FileInputStream fstream = new FileInputStream(driverFile);
            ArrayList<String> driverFunctionName = new ArrayList<String>();
            DataInputStream in = new DataInputStream(fstream);
            BufferedReader br = new BufferedReader(new InputStreamReader(in));
            String strLine;
            while ((strLine = br.readLine()) != null) {
                Pattern casePattern = Pattern.compile("^CASE\\s+(\\d+)");
                Matcher match = casePattern.matcher(strLine);
                while (match.find()) {
                    driverFunctionName.add(match.group());
                    caseId = match.group();
                    strLine = br.readLine();
                    casePattern = Pattern.compile("NAME\\s+(\\\"+(.*)\\\")");
                    match = casePattern.matcher(strLine);
                    if (match.find()) {
                        caseName = match.group(2);
                    }
                    testCaseIdAndName.put(caseId, caseName);
                }
            }
        } catch (Exception e) {
        }
    }

    public void getParamsUpdate(String testcases) {
        try {
            File file = new File(paramFileName);
            BufferedReader reader = new BufferedReader(new FileReader(file));
            String line = "", oldtext = "";
            while ((line = reader.readLine()) != null) {
                oldtext += line + "\r\n";
            }
            reader.close();
            String newtext = oldtext.replaceAll("<testcases>\\s*(\\d+)</testcases>", "<testcases>" + testcases + "</testcases>");
            FileWriter writer = new FileWriter(paramFileName);
            writer.write(newtext);
            writer.close();
        } catch (IOException ioe) {
            ioe.printStackTrace();
        }
    }

    public TreeMap getCaseIdAndName() {
        return testCaseIdAndName;
    }

    public void getTestSteps(String caseNumber) {
        OFAFileOperations fileOperation = new OFAFileOperations();
        int stepCount = 0;
        String stepCounter = "";
        BufferedReader input = null;
        ArrayList<String> contents = new ArrayList<String>();
        File scriptName = new File(driverFile);
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
                    input = new BufferedReader(new FileReader(pythonFile));
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
}
