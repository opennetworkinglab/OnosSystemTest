/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package tai_ofa;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.geometry.Side;
import javafx.scene.Group;
import javafx.scene.control.ContextMenu;
import javafx.scene.control.Label;
import javafx.scene.control.ListView;
import javafx.scene.control.MenuItem;
import javafx.scene.control.TextField;
import javafx.scene.input.KeyCode;
import javafx.scene.input.KeyEvent;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.StackPane;

/**
 *
 * @author Raghav kashyap (raghavkashyap@paxterrasolutions.com)
	
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
public class OFAContentHelp {

    ContextMenu assertContext;
    ArrayList<MenuItem> assertNameList;
    CodeEditor Content;
    TAI_OFA OFAReference;
    String ospkCommand;
    boolean keyPressed = false;
    ArrayList<String> checkBuffer;
    ContextMenu contextMenu, driverFunctionContextMenu;
    ArrayList<String> myDevices;
    ArrayList<MenuItem> myMenuItems;
    ArrayList<String> driverFunctionName;
    ArrayList<MenuItem> functionMenuItem;
    OFAParamDeviceName paramFile;
    String deviceTypePath;
    ContextMenu commandNameContextMenu, withContextMenu, runDriverContextMenu;
    ArrayList<MenuItem> bdtFunction;
    String selectedDeviceName;
    String selectedFunctionName;
    TextField paraMeterListText;
    ArrayList<String> parameterArrayList = new ArrayList<String>();
    ArrayList<TextField> parameterTextFieldList = new ArrayList<TextField>();
    String matchedCase;
    ArrayList<Label> parameterLabel = new ArrayList<Label>();
    OFAFileOperations fileOperation = new OFAFileOperations();
    ObservableList<String> data;
    Group popupRoot;
    ListView<String> seleniumFunctionListView, cliFunctionListView;
    String baseDeviceDriver, cliFunctionStr;
    ArrayList<String> cliFunctionList = new ArrayList<String>();
    HashMap<String, String> cliFunctionWithArgumentMap = new HashMap<String, String>();
    String selectedCLiFunction;
    String selectedSeleniumFunction;
    TAILocale label = new TAILocale(new Locale("en", "EN"));
    String OFAHarnessPath = label.hierarchyTestON;
    String bdrPath;
    String selectedDeviceType;

    public OFAContentHelp() {
    }

    public OFAContentHelp(CodeEditor editor, TAI_OFA reference) {
        this.Content = editor;
        OFAReference = reference;
    }

    public void assertContextMenu() {
        assertContext = new ContextMenu();
        MenuItem equal = new MenuItem("EQUALS");
        MenuItem match = new MenuItem("MATCHES");
        MenuItem greater = new MenuItem("GREATER");
        MenuItem lesser = new MenuItem("LESSER");
        assertNameList = new ArrayList<MenuItem>();
        assertNameList.add(equal);
        assertNameList.add(match);
        assertNameList.add(greater);
        assertNameList.add(lesser);
        assertContext.getItems().addAll(equal, match, greater, lesser);
    }

    public void ospkHelp() {

        Content.addEventHandler(KeyEvent.KEY_PRESSED, new EventHandler<KeyEvent>() {
            @Override
            public void handle(KeyEvent keyEvent) {
                if (keyEvent.getCode() == KeyCode.SPACE) {
                    ArrayList<Integer> existingCaseNumber = new ArrayList<Integer>();
                    existingCaseNumber.add(0);
                    String[] content = Content.getCodeAndSnapshot().split("\n");
                    for (int i = 0; i < content.length; i++) {
                        Pattern pattern = Pattern.compile("CASE\\s+(\\d+)\\s*");
                        Matcher matchCase = pattern.matcher(content[i]);

                        while (matchCase.find()) {
                            try {
                                int number = Integer.parseInt(matchCase.group(1));
                                existingCaseNumber.add(number);
                            } catch (Exception e) {
                            }
                        }
                    }

                    int max = Collections.max(existingCaseNumber);
                    max = max + 1;
                    String caseNumbers = String.valueOf(max);
                    Content.setLine(Integer.parseInt(Content.getCurrentLineNumber()), Content.getCurrentLine().replace("CASE", "CASE" + " " + caseNumbers));
                }

                Pattern namePattern = Pattern.compile("\\s*NAME\\s+(.*)");
                Pattern descPattern = Pattern.compile("DESC\\s+(.*)");
                Pattern stepPattern = Pattern.compile("STEP\\s+(.*)");
                Pattern onPattern = Pattern.compile("ON\\s+(.*)");
                Pattern cmdPattern = Pattern.compile("ON\\s+(\\w+\\s+(.*))");
                Pattern runPattern = Pattern.compile("" + ospkCommand + "\\s+(.*)");
                Pattern assertPattern = Pattern.compile("ASSERT\\s+(.*)");
                Pattern usingPattern = Pattern.compile("(.*)\\s+USING\\s+");
                String[] OFAEditorLine = Content.getCodeAndSnapshot().split("\n");

                final Matcher onMatch = onPattern.matcher(Content.getCurrentLine());
                final Matcher cmdMatch = cmdPattern.matcher(Content.getCurrentLine());
                final Matcher runMatch = runPattern.matcher(Content.getCurrentLine());
                final Matcher asertMatch = assertPattern.matcher(Content.getCurrentLine());
                final Matcher usingMatch = usingPattern.matcher(Content.getCurrentLine());
                Matcher nameMatch = namePattern.matcher(Content.getCurrentLine());
                Matcher descMatch = descPattern.matcher(Content.getCurrentLine());
                Matcher stepMatch = stepPattern.matcher(Content.getCurrentLine());
                while (nameMatch.find()) {
                    if (nameMatch.group(1).isEmpty()) {
                        if (keyEvent.getCode() == KeyCode.SPACE) {
                            Content.setLine(Integer.parseInt(Content.getCurrentLineNumber()), Content.getCurrentLine().replace("NAME", "NAME" + " " + "\"\""));
                        }

                    }
                }

                while (descMatch.find()) {
                    if (descMatch.group(1).isEmpty()) {
                        if (keyEvent.getCode() == KeyCode.SPACE) {
                            Content.setLine(Integer.parseInt(Content.getCurrentLineNumber()), Content.getCurrentLine().replace("DESC", "DESC" + " " + "\"\""));
                        }

                    }
                }

                while (stepMatch.find()) {
                    if (stepMatch.group(1).isEmpty()) {
                        if (keyEvent.getCode() == KeyCode.SPACE) {
                            Content.setLine(Integer.parseInt(Content.getCurrentLineNumber()), Content.getCurrentLine().replace("STEP", "STEP" + " " + "\"\""));
                        }

                    }
                }


                while (onMatch.find()) {
                    if (onMatch.group(1).isEmpty()) {
                        if (keyEvent.getCode() == KeyCode.getKeyCode("Ctrl")) {
                            keyPressed = true;
                        }

                        if (keyPressed == true) {
                            if (keyEvent.getCode() == KeyCode.SPACE) {
                                keyPressed = false;
                                onMatch.group();
                                onDeviceContextMenu();
                                contextMenu.show(OFAReference.editorTabPane, Side.TOP, Content.cursorPosfromLeft(), Content.cursorPosfromTop() + 65);
                                for (final MenuItem myMenuItem : myMenuItems) {
                                    myMenuItem.setOnAction(new EventHandler<ActionEvent>() {
                                        @Override
                                        public void handle(ActionEvent arg0) {
                                            HashMap<String, String> deviceNameAndType = paramFile.getdeviceNameAndType();
                                            Iterator paramIterator = deviceNameAndType.entrySet().iterator();
                                            while (paramIterator.hasNext()) {
                                                Map.Entry mEntry = (Map.Entry) paramIterator.next();
                                                if (myMenuItem.getText().equals(mEntry.getKey())) {
                                                    selectedDeviceType = mEntry.getValue().toString();
                                                    selectedDeviceType = selectedDeviceType.replaceAll("\\s+", "");
                                                    String driverTypePath = OFAHarnessPath + "/drivers/common/";
                                                    File aFile = new File(driverTypePath);
                                                    fileOperation.Process(aFile);
                                                    for (String path : fileOperation.filePath) {
                                                        String[] splitPath = path.split("\\/");
                                                        String[] fileName = splitPath[splitPath.length - 1].split("\\.");
                                                        for (int p = 0; p < fileName.length; p++) {
                                                            if ((selectedDeviceType).equals(fileName[p])) {
                                                                deviceTypePath = path;
                                                                bdrPath = deviceTypePath.replaceAll("py", "ospk");
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                            selectedDeviceName = myMenuItem.getText();
                                            Content.setLine(Integer.parseInt(Content.getCurrentLineNumber()), Content.getCurrentLine().replace("ON", "ON" + " " + myMenuItem.getText()));
                                        }
                                    });
                                }
                            }
                        }

                    }
                }
                while (cmdMatch.find()) {
                    if (cmdMatch.group(2).isEmpty()) {
                        if (keyEvent.getCode() == KeyCode.getKeyCode("Ctrl")) {
                            keyPressed = true;
                        }

                        if (keyPressed == true) {
                            if (keyEvent.getCode() == KeyCode.SPACE) {
                                runContextMenu();
                                commandNameContextMenu.show(OFAReference.editorTabPane, Side.TOP, Content.cursorPosfromLeft(), Content.cursorPosfromTop() + 115);
                                for (final MenuItem bdtCmd : bdtFunction) {
                                    bdtCmd.setOnAction(new EventHandler<ActionEvent>() {
                                        @Override
                                        public void handle(ActionEvent t) {
                                            ospkCommand = bdtCmd.getText();
                                            Content.setLine(Integer.parseInt(Content.getCurrentLineNumber()), Content.getCurrentLine().replace(selectedDeviceName, selectedDeviceName + " " + bdtCmd.getText()));
                                        }
                                    });
                                }
                            }
                        }
                    }
                }

                while (runMatch.find()) {

                    if (runMatch.group(1).isEmpty()) {
                        if (keyEvent.getCode() == KeyCode.getKeyCode("Ctrl")) {
                            keyPressed = true;
                        }
                        if (keyPressed == true) {
                            if (keyEvent.getCode() == KeyCode.SPACE) {
                                keyPressed = false;

                                onDriverContextMenu();
                                driverFunctionContextMenu.show(OFAReference.editorTabPane, Side.TOP, Content.cursorPosfromLeft(), Content.cursorPosfromTop() + 65);

                                Group popupRoot = (Group) driverFunctionContextMenu.getScene().getRoot();
                                final ListView<String> driverFunctionListView = new ListView<String>();
                                data = FXCollections.observableArrayList();
                                for (String function : driverFunctionName) {
                                    data.add(function);
                                }
                                driverFunctionListView.setItems(data);
                                driverFunctionListView.setMaxHeight(100);
                                driverFunctionListView.setMaxWidth(150);
                                driverFunctionListView.getSelectionModel().selectFirst();

                                driverFunctionListView.addEventFilter(KeyEvent.KEY_PRESSED, new EventHandler<KeyEvent>() {
                                    @Override
                                    public void handle(KeyEvent arg0) {
                                        if (arg0.getCode() == KeyCode.ENTER || arg0.getCode() == KeyCode.SPACE) {
                                            selectedFunctionName = driverFunctionListView.getSelectionModel().getSelectedItem().toString();
                                            Content.setLine(Integer.parseInt(Content.getCurrentLineNumber()), Content.getCurrentLine().replace("RUN", "RUN" + " " + selectedFunctionName));
                                            driverFunctionContextMenu.hide();
                                        }
                                    }
                                });
                                popupRoot.getChildren().add(driverFunctionListView);
                                driverFunctionListView.requestFocus();
                            }
                        }
                    }
                }

                while (asertMatch.find()) {
                    if (asertMatch.group(1).isEmpty()) {
                        if (keyEvent.getCode() == KeyCode.getKeyCode("Ctrl")) {
                            keyPressed = true;
                        }

                        if (keyPressed == true) {
                            if (keyEvent.getCode() == KeyCode.SPACE) {
                                OFAContentHelp contentHelp = new OFAContentHelp();
                                contentHelp.assertContextMenu();
                                contentHelp.assertContext.show(OFAReference.editorTabPane, Side.TOP, Content.cursorPosfromLeft(), Content.cursorPosfromTop() + 65);
                                for (final MenuItem assertCommand : contentHelp.assertNameList) {
                                    assertCommand.setOnAction(new EventHandler<ActionEvent>() {
                                        @Override
                                        public void handle(ActionEvent t) {
                                            Content.setLine(Integer.parseInt(Content.getCurrentLineNumber()), Content.getCurrentLine().replace("ASSERT", "ASSERT " + assertCommand.getText()));
                                        }
                                    });
                                }
                            }
                        }
                    }

                }

                while (usingMatch.find()) {
                    if (!usingMatch.group(1).isEmpty()) {
                        if (keyEvent.getCode() == KeyCode.CONTROL) {
                            keyPressed = true;
                        }

                        if (keyPressed == true) {
                            if (keyEvent.getCode() == KeyCode.SPACE) {
                                OFAParamDeviceName paramDeice = new OFAParamDeviceName();
                                if (selectedDeviceType.equals("poxclidriver")) {
                                    String baseCliDevice = bdrPath.replace(bdrPath, label.hierarchyTestON + "/drivers/common/cli/emulator/poxclidriver.py");
                                    paramDeice.driverFunctionName(baseCliDevice);
                                    for (String functionName : paramDeice.driverFunctionName) {
                                        driverFunctionName.add(functionName);
                                    }
                                } else if (selectedDeviceType.equals("mininetclidriver")) {
                                    String baseCliDevice = bdrPath.replace(bdrPath, label.hierarchyTestON + "/drivers/common/cli/emulator/mininetclidriver.py");
                                    paramDeice.driverFunctionName(baseCliDevice);
                                    for (String functionName : paramDeice.driverFunctionName) {
                                        driverFunctionName.add(functionName);
                                    }
                                } else if (selectedDeviceType.equals("hpswitchclidriver")) {
                                    String baseCliDevice = bdrPath.replace(bdrPath, label.hierarchyTestON + "/drivers/common/cli/remotetestbed/hpswitchclidriver.py");
                                    paramDeice.driverFunctionName(baseCliDevice);
                                    for (String functionName : paramDeice.driverFunctionName) {
                                        driverFunctionName.add(functionName);
                                    }
                                }
                                if (selectedDeviceType.equals("flowvisorclidriver")) {
                                    String baseCliDevice = bdrPath.replace(bdrPath, label.hierarchyTestON + "/drivers/common/cli/remotesys/flowvisorclidriver.py");
                                    paramDeice.driverFunctionName(baseCliDevice);
                                    for (String functionName : paramDeice.driverFunctionName) {
                                        driverFunctionName.add(functionName);
                                    }
                                }
                                if (selectedDeviceType.equals("floodlightclidriver")) {
                                    String baseCliDevice = bdrPath.replace(bdrPath, label.hierarchyTestON + "/drivers/common/cli/remotesys/floodlightclidriver.py");
                                    paramDeice.driverFunctionName(baseCliDevice);
                                    for (String functionName : paramDeice.driverFunctionName) {
                                        driverFunctionName.add(functionName);
                                    }
                                }
                                if (selectedDeviceType.equals("remotepoxdriver")) {
                                    String baseCliDevice = bdrPath.replace(bdrPath, label.hierarchyTestON + "/drivers/common/cli/remotesys/remotepoxdriver.py");
                                    paramDeice.driverFunctionName(baseCliDevice);
                                    for (String functionName : paramDeice.driverFunctionName) {
                                        driverFunctionName.add(functionName);
                                    }
                                }
                                if (selectedDeviceType.equals("remotevmdriver")) {
                                    String baseCliDevice = bdrPath.replace(bdrPath, label.hierarchyTestON + "/drivers/common/cli/remotesys/remotevmdriver.py");
                                    paramDeice.driverFunctionName(baseCliDevice);
                                    for (String functionName : paramDeice.driverFunctionName) {
                                        driverFunctionName.add(functionName);
                                    }
                                }
                                if (selectedDeviceType.equals("dpctlclidriver")) {
                                    String baseCliDevice = bdrPath.replace(bdrPath, label.hierarchyTestON + "/drivers/common/cli/tool/dpctlclidriver.py");
                                    paramDeice.driverFunctionName(baseCliDevice);
                                    for (String functionName : paramDeice.driverFunctionName) {
                                        driverFunctionName.add(functionName);
                                    }
                                }
                                if (selectedDeviceType.equals("fvtapidriver")) {
                                    String baseCliDevice = bdrPath.replace(bdrPath, label.hierarchyTestON + "/drivers/common/api/fvtapidriver.py");
                                    paramDeice.driverFunctionName(baseCliDevice);
                                    for (String functionName : paramDeice.driverFunctionName) {
                                        driverFunctionName.add(functionName);
                                    }
                                }
                                HashMap<String, String> functionAndParameter = paramDeice.functionWithParameter;
                                Set set = functionAndParameter.entrySet();
                                // Get an iterator
                                Iterator functionAndParameterIterator = set.iterator();
                                // Display elements
                                final GridPane paramPanel = new GridPane();
                                paramPanel.setStyle("-fx-background-color: DAE6F3;");
                                String caseParameter = "";
                                parameterLabel.clear();
                                parameterTextFieldList.clear();
                                while (functionAndParameterIterator.hasNext()) {
                                    Map.Entry functionInfo = (Map.Entry) functionAndParameterIterator.next();
                                    if (selectedFunctionName.equals(functionInfo.getKey().toString())) {
                                        String[] splitParameter = functionInfo.getValue().toString().split("\\,");
                                        if (splitParameter.length > 0) {
                                            for (int j = 0; j < splitParameter.length; j++) {
                                                Label parameterList = new Label();
                                                parameterLabel.add(parameterList);
                                                paraMeterListText = new TextField();
                                                parameterList.setText(splitParameter[j]);
                                                paramPanel.add(parameterList, 0, j);
                                                paramPanel.add(paraMeterListText, 1, j);
                                                parameterTextFieldList.add(paraMeterListText);
                                                caseParameter += splitParameter[j].toLowerCase() + "AS " + "CASE" + "[" + splitParameter[j].toLowerCase() + "]" + ",";
                                            }
                                        }
                                    }
                                }
                                withContextMenu();
                                withContextMenu.show(OFAReference.editorTabPane, Side.TOP, Content.cursorPosfromLeft(), Content.cursorPosfromTop() + 65);
                                Group popupRoot = (Group) withContextMenu.getScene().getRoot();
                                Group popupCSSBridge = (Group) popupRoot.getChildren().get(0);
                                StackPane popupContent = (StackPane) popupCSSBridge.getChildren().get(0);
                                popupRoot.getChildren().add(paramPanel);
                                if (!caseParameter.equals("")) {
                                    try {
                                        caseParameter = caseParameter.substring(0, caseParameter.length() - 1);
                                    } catch (ArrayIndexOutOfBoundsException e) {
                                    }
                                }
                                popupContent.setMaxHeight(OFAReference.editorTabPane.getHeight() - 400);
                                Content.setLine(Integer.parseInt(Content.getCurrentLineNumber()), Content.getCurrentLine().replace("USING", "USING" + " " + caseParameter));
                                for (int k = Integer.parseInt(Content.getCurrentLineNumber()); k > 0; k--) {
                                    Pattern firstUpperCasePattern = Pattern.compile("CASE\\s+(\\d)");
                                    Matcher firstUpperCaseMatch = firstUpperCasePattern.matcher(Content.getCurrentLine(k));
                                    if (firstUpperCaseMatch.find()) {
                                        matchedCase = firstUpperCaseMatch.group();
                                        break;
                                    }
                                }
                                try {
                                    paraMeterListText.setOnKeyPressed(new EventHandler<KeyEvent>() {
                                        @Override
                                        public void handle(KeyEvent keyEvent) {
                                            if (keyEvent.getCode() == KeyCode.ENTER) {
                                                String paramCaseContent = "";
                                                String matchCaseWithoutSpace = matchedCase.replaceAll("\\s+", "");
                                                String currentTabPath = OFAReference.editorTabPane.getSelectionModel().getSelectedItem().getId();
                                                String paramFile = currentTabPath.replace(fileOperation.getExtension(currentTabPath), ".params");
                                                Pattern matchCasePattern = Pattern.compile("^\\s*\\<" + matchCaseWithoutSpace + "\\>");
                                                String fileContent[] = fileOperation.getContents(new File(paramFile)).split("\n");
                                                String myCase = "";
                                                Boolean caseFlag = false;
                                                int k;
                                                for (k = 0; k < fileContent.length; k++) {
                                                    Matcher caseMatch = matchCasePattern.matcher(fileContent[k]);
                                                    if (caseMatch.find()) {
                                                        myCase = caseMatch.group();
                                                        caseFlag = true;
                                                        break;
                                                    }
                                                }
                                                if (caseFlag == true) {
                                                    String remainingConetent = "";
                                                    int caseVarible = k;
                                                    k++;
                                                    for (; k < fileContent.length; k++) {
                                                        remainingConetent += "\n" + fileContent[k];
                                                    }
                                                    String allContent = "";
                                                    allContent += fileContent[0];
                                                    for (int p = 1; p < caseVarible; p++) {
                                                        allContent += "\n" + fileContent[p];
                                                    }
                                                    allContent += "\n\t<" + matchCaseWithoutSpace + ">";

                                                    for (int i = 0; i < parameterTextFieldList.size(); i++) {
                                                        String parameterLabels = parameterLabel.get(i).getText().replaceAll("\"", "");
                                                        paramCaseContent += "\n\t\t<" + parameterLabels.toLowerCase() + ">" + parameterTextFieldList.get(i).getText() + "</" + parameterLabels.toLowerCase() + ">";
                                                    }

                                                    allContent += paramCaseContent;
                                                    allContent += remainingConetent;
                                                    String paramFilePath = OFAReference.editorTabPane.getSelectionModel().getSelectedItem().getId().replace(fileOperation.getExtension(OFAReference.editorTabPane.getSelectionModel().getSelectedItem().getId()), ".params");
                                                    String paramFileContent = fileOperation.getContents(new File(paramFilePath));
                                                    try {
                                                        fileOperation.setContents(new File(paramFilePath), allContent);
                                                    } catch (FileNotFoundException ex) {
                                                        Logger.getLogger(OFAContentHelp.class.getName()).log(Level.SEVERE, null, ex);
                                                    } catch (IOException ex) {
                                                        Logger.getLogger(OFAContentHelp.class.getName()).log(Level.SEVERE, null, ex);
                                                    }
                                                    withContextMenu.hide();
                                                    paramPanel.setVisible(false);
                                                } else {
                                                    paramCaseContent += "<" + matchCaseWithoutSpace + ">";
                                                    for (int i = 0; i < parameterTextFieldList.size(); i++) {
                                                        paramCaseContent += "\n\t\t<" + parameterLabel.get(i).getText().toLowerCase() + ">" + parameterTextFieldList.get(i).getText() + "</" + parameterLabel.get(i).getText().toLowerCase() + ">";
                                                    }

                                                    paramCaseContent += "\n\t" + "</" + matchCaseWithoutSpace + ">";
                                                    String paramFilePath = OFAReference.editorTabPane.getSelectionModel().getSelectedItem().getId().replace(fileOperation.getExtension(OFAReference.editorTabPane.getSelectionModel().getSelectedItem().getId()), ".params");
                                                    String paramFileContent = fileOperation.getContents(new File(paramFilePath));
                                                    String removeTestParam = paramFileContent.replace("</TEST_PARAMS>", " ");
                                                    removeTestParam += "\t" + paramCaseContent + "\n\n" + "</TEST_PARAMS>";
                                                    try {
                                                        fileOperation.setContents(new File(paramFilePath), removeTestParam);
                                                    } catch (FileNotFoundException ex) {
                                                        Logger.getLogger(OFAContentHelp.class.getName()).log(Level.SEVERE, null, ex);
                                                    } catch (IOException ex) {
                                                        Logger.getLogger(OFAContentHelp.class.getName()).log(Level.SEVERE, null, ex);
                                                    }
                                                    withContextMenu.hide();
                                                    paramPanel.setVisible(false);
                                                }
                                            }
                                        }
                                    });
                                } catch (Exception e) {
                                }

                            }
                        }
                    }

                }

                checkBuffer = new ArrayList<String>();

                if (keyEvent.getCode() == KeyCode.ENTER) {
                    String bufferedString = "";
                    for (String s : checkBuffer) {
                        bufferedString += s;
                    }
                    Pattern pattern = Pattern.compile("CASE\\s+(\\d+)");
                    Matcher match = pattern.matcher(bufferedString);
                    while (match.find()) {
                        Content.setCode(Content.getCodeAndSnapshot().replaceAll(bufferedString, bufferedString + "\n\n" + "END CASE"));
                    }
                    checkBuffer.clear();
                }

            }
        });

        Content.setOnKeyPressed(new EventHandler<KeyEvent>() {
            @Override
            public void handle(KeyEvent arg0) {
                String text = arg0.getText();
                if (arg0.getCode() == KeyCode.ENTER) {
                } else if (arg0.getCode() == KeyCode.BACK_SPACE) {
                } else {
                    checkBuffer.add(text);
                }
            }
        });
    }

    public void onDeviceContextMenu() {
        contextMenu = new ContextMenu();
        myDevices = new ArrayList<String>();
        ArrayList<String> paramDeviceType = new ArrayList<String>();
        myMenuItems = new ArrayList<MenuItem>();

        String selectedTabPath = OFAReference.editorTabPane.getSelectionModel().getSelectedItem().getId();
        String[] splitSelectedPath = selectedTabPath.split("\\/");
        String[] ospkFileName = splitSelectedPath[splitSelectedPath.length - 1].toString().split("\\.");
        String paramFileName = ospkFileName[0] + ".topo";
        String paramFilePath = selectedTabPath.replace(splitSelectedPath[splitSelectedPath.length - 1].toString(), paramFileName);
        paramFile = new OFAParamDeviceName(paramFilePath, "");
        paramFile.parseParamFile();

        for (String deviceName : paramFile.getParamDeviceName()) {
            myDevices.add(deviceName);
        }

        for (String myDevice : myDevices) {
            final MenuItem myMenuItem = new MenuItem(myDevice);
            myMenuItem.setOnAction(new EventHandler<ActionEvent>() {
                @Override
                public void handle(ActionEvent arg0) {
                }
            });
            myMenuItems.add(myMenuItem);
        }

        for (MenuItem myMenuItem : myMenuItems) {
            contextMenu.getItems().addAll(myMenuItem);

        }

        OFAReference.editorTabPane.setContextMenu(contextMenu);
    }

    public void onDriverContextMenu() {
        driverFunctionContextMenu = new ContextMenu();
        driverFunctionName = new ArrayList<String>();
        driverFunctionName.clear();
        OFAParamDeviceName driverFile = new OFAParamDeviceName();

        if (selectedDeviceType.equals("poxclidriver")) {
            String baseCliDevice = bdrPath.replace(bdrPath, label.hierarchyTestON + "/drivers/common/cli/emulator/poxclidriver.py");
            driverFile.driverFunctionName(baseCliDevice);
            for (String functionName : driverFile.driverFunctionName) {
                driverFunctionName.add(functionName);
            }
        } else if (selectedDeviceType.equals("mininetclidriver")) {
            String baseCliDevice = bdrPath.replace(bdrPath, label.hierarchyTestON + "/drivers/common/cli/emulator/mininetclidriver.py");
            driverFile.driverFunctionName(baseCliDevice);
            for (String functionName : driverFile.driverFunctionName) {
                driverFunctionName.add(functionName);
            }
        }
        if (selectedDeviceType.equals("hpswitchdriver")) {
            String baseCliDevice = bdrPath.replace(bdrPath, label.hierarchyTestON + "/drivers/common/cli/remotesys/hpswitchdriver.py");
            driverFile.driverFunctionName(baseCliDevice);
            for (String functionName : driverFile.driverFunctionName) {
                driverFunctionName.add(functionName);
            }
        }
        if (selectedDeviceType.equals("dpctlclidriver")) {
            String baseCliDevice = bdrPath.replace(bdrPath, label.hierarchyTestON + "/drivers/common/cli/tool/dpctlclidriver.py");
            driverFile.driverFunctionName(baseCliDevice);
            for (String functionName : driverFile.driverFunctionName) {
                driverFunctionName.add(functionName);
            }
        }
        if (selectedDeviceType.equals("fvtapidriver")) {
            String baseCliDevice = bdrPath.replace(bdrPath, label.hierarchyTestON + "/drivers/common/api/fvtapidriver.py");
            driverFile.driverFunctionName(baseCliDevice);
            for (String functionName : driverFile.driverFunctionName) {
                driverFunctionName.add(functionName);
            }
        } else if (selectedDeviceType.equals("hpswitchclidriver")) {
            String baseCliDevice = bdrPath.replace(bdrPath, label.hierarchyTestON + "/drivers/common/cli/remotetestbed/hpswitchclidriver.py");
            driverFile.driverFunctionName(baseCliDevice);
            for (String functionName : driverFile.driverFunctionName) {
                driverFunctionName.add(functionName);
            }
        }
        if (selectedDeviceType.equals("flowvisorclidriver")) {
            String baseCliDevice = bdrPath.replace(bdrPath, label.hierarchyTestON + "/drivers/common/cli/remotetestbed/flowvisorclidriver.py");
            driverFile.driverFunctionName(baseCliDevice);
            for (String functionName : driverFile.driverFunctionName) {
                driverFunctionName.add(functionName);
            }
        }
        if (selectedDeviceType.equals("floodlightclidriver")) {
            String baseCliDevice = bdrPath.replace(bdrPath, label.hierarchyTestON + "/drivers/common/cli/remotetestbed/floodlightclidriver.py");
            driverFile.driverFunctionName(baseCliDevice);
            for (String functionName : driverFile.driverFunctionName) {
                driverFunctionName.add(functionName);
            }
        }
        if (selectedDeviceType.equals("remotepoxdriver")) {
            String baseCliDevice = bdrPath.replace(bdrPath, label.hierarchyTestON + "/drivers/common/cli/remotetestbed/remotepoxdriver.py");
            driverFile.driverFunctionName(baseCliDevice);
            for (String functionName : driverFile.driverFunctionName) {
                driverFunctionName.add(functionName);
            }
        }
        if (selectedDeviceType.equals("remotevmdriver")) {
            String baseCliDevice = bdrPath.replace(bdrPath, label.hierarchyTestON + "/drivers/common/cli/remotetestbed/remotevmdriver.py");
            driverFile.driverFunctionName(baseCliDevice);
            for (String functionName : driverFile.driverFunctionName) {
                driverFunctionName.add(functionName);
            }
        }
        driverFunctionContextMenu.getItems().add(new MenuItem());
    }

    public void runContextMenu() {
        commandNameContextMenu = new ContextMenu();
        MenuItem run = new MenuItem("RUN");
        MenuItem exec = new MenuItem("EXEC");
        MenuItem config = new MenuItem("CONFIG");
        bdtFunction = new ArrayList<MenuItem>();
        bdtFunction.add(run);
        bdtFunction.add(exec);
        bdtFunction.add(config);
        commandNameContextMenu.getItems().addAll(run, exec, config);
    }

    public void withContextMenu() {
        withContextMenu = new ContextMenu();
        MenuItem item = new MenuItem();
        withContextMenu.getItems().add(item);
        item.setDisable(true);
    }

    // drivers context menu
    public void runDriverContextMenu() {
        runDriverContextMenu = new ContextMenu();
        MenuItem runDriverMenuItem = new MenuItem("");
        runDriverContextMenu.getItems().add(runDriverMenuItem);
    }
}
