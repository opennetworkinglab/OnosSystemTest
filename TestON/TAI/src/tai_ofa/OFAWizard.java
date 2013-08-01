/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package tai_ofa;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Path;
import java.security.acl.Owner;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Locale;
import java.util.Map;
import java.util.Observable;
import java.util.Set;
import java.util.Stack;
import java.util.logging.Level;
import java.util.logging.Logger;
import javafx.application.Application;
import javafx.beans.property.DoubleProperty;
import javafx.beans.value.ChangeListener;
import javafx.beans.value.ObservableValue;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.geometry.Insets;
import javafx.geometry.Orientation;
import javafx.geometry.Side;
import javafx.scene.Cursor;
import javafx.scene.Node;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.ComboBox;
import javafx.scene.control.ComboBoxBuilder;
import javafx.scene.control.ContextMenu;
import javafx.scene.control.Label;
import javafx.scene.control.MenuItem;
import javafx.scene.control.MultipleSelectionModel;
import javafx.scene.control.Separator;
import javafx.scene.control.SingleSelectionModel;
import javafx.scene.control.Tab;
import javafx.scene.control.TabPane;
import javafx.scene.control.TextField;
import javafx.scene.control.TextFieldBuilder;
import javafx.scene.control.ToolBar;
import javafx.scene.control.Tooltip;
import javafx.scene.control.TreeItem;
import javafx.scene.control.TreeView;
import javafx.scene.effect.DropShadow;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.input.ClipboardContent;
import javafx.scene.input.DragEvent;
import javafx.scene.input.Dragboard;
import javafx.scene.input.KeyEvent;
import javafx.scene.input.MouseButton;
import javafx.scene.input.MouseDragEvent;
import javafx.scene.input.MouseEvent;
import javafx.scene.input.TransferMode;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.BorderPaneBuilder;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.GridPaneBuilder;
import javafx.scene.layout.HBox;
import javafx.scene.layout.Pane;
import javafx.scene.layout.Priority;
import javafx.scene.layout.Region;
import javafx.scene.layout.StackPane;
import javafx.scene.layout.VBox;
import javafx.scene.paint.Color;
import javafx.scene.shape.Circle;
import javafx.scene.shape.Line;
import javafx.scene.shape.StrokeLineCap;
import javafx.scene.text.Font;
import javafx.scene.text.FontWeight;
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
public class OFAWizard extends Application {

    NewWizard wizard;
    TAI_OFA referenceOFA;

    public OFAWizard() {
    }
    TreeItem<String> rootItem;
    TreeItem<String> testTree;
    ObservableList<TreeItem<String>> listProject;
    TreeView<String> projectTree;
    int caseNumber;
    String paramsFileName;

    public OFAWizard(TreeItem<String> root, int i, ObservableList<TreeItem<String>> listProject1, TreeView<String> projectTree1) {
        rootItem = root;
        caseNumber = i;
        listProject = listProject1;
        projectTree = projectTree1;
    }

    public void setOFA(TAI_OFA ofa) {
        this.referenceOFA = ofa;
    }

    @Override
    public void start(Stage stage) throws Exception {
        wizard = new NewWizard(stage, rootItem, referenceOFA, caseNumber, listProject, projectTree);
        stage.setTitle("TestON - Automation is O{pe}N ");
        Scene scene = new Scene(wizard, 700, 400);
        stage.setScene(scene);
        stage.setResizable(false);
        scene.getStylesheets().addAll(this.getClass().getResource("wizard.css").toExternalForm());
        paramsFileName = wizard.paramsFileName;
        stage.show();
    }

    public void setProjectList(ObservableList<TreeItem<String>> list) {
        listProject = list;
    }

    public void setProjectView(TreeView<String> tree) {
        projectTree = tree;
    }
}

/**
 * basic wizard infrastructure class
 */
class Wizard extends StackPane {

    private static final int UNDEFINED = -1;
    private ObservableList<WizardPage> pages = FXCollections.observableArrayList();
    private Stack<Integer> history = new Stack();
    private int curPageIdx = UNDEFINED;
    NewWizard newWizardObjct;

    public Wizard() {
    }

    void setAllData(WizardPage... nodes) {
        for (WizardPage wizardPage : nodes) {
            wizardPage.setNewWizard(newWizardObjct);
            pages.add(wizardPage);
        }
        navTo(0);
        setStyle("-fx-padding: 0; -fx-background-color: cornsilk;");
    }

    Wizard(WizardPage... nodes) {
        for (WizardPage wizardPage : nodes) {
            wizardPage.setNewWizard(newWizardObjct);
            pages.add(wizardPage);
        }
        navTo(0);
        setStyle("-fx-padding: 0; -fx-background-color: cornsilk;");
    }

    ObservableList<WizardPage> getAllChildrens() {
        return pages;
    }

    void nextPage() {
        if (hasNextPage()) {
            navTo(curPageIdx + 1);
        }
    }

    void priorPage() {
        if (hasPriorPage()) {
            navTo(history.pop(), false);
        }
    }

    boolean hasNextPage() {
        return (curPageIdx < pages.size() - 1);
    }

    boolean hasPriorPage() {
        return !history.isEmpty();
    }

    void navTo(int nextPageIdx, boolean pushHistory) {
        if (nextPageIdx < 0 || nextPageIdx >= pages.size()) {
            return;
        }
        if (curPageIdx != UNDEFINED) {
            if (pushHistory) {
                history.push(curPageIdx);
            }
        }

        WizardPage nextPage = pages.get(nextPageIdx);
        curPageIdx = nextPageIdx;
        getChildren().clear();
        getChildren().add(nextPage);
        nextPage.manageButtons();
    }

    void navTo(int nextPageIdx) {
        navTo(nextPageIdx, true);
    }

    void navTo(String id) {
        Node page = lookup("#" + id);
        if (page != null) {
            int nextPageIdx = pages.indexOf(page);
            if (nextPageIdx != UNDEFINED) {
                navTo(nextPageIdx);
            }
        }
    }

    public void finish() {
    }

    public void cancel() {
    }

    public void setNewWizard(NewWizard newWizardObj) {
        newWizardObjct = newWizardObj;
    }
}

/**
 * basic wizard page class
 */
abstract class WizardPage extends VBox {

    TAILocale label = new TAILocale(new Locale("en", "EN"));
    Button priorButton = new Button("<< Previous");
    Button nextButton = new Button("Next >>");
    Button cancelButton = new Button("Cancel");
    Button finishButton = new Button("Finish");
    NewWizard newWizardReference;

    WizardPage(String title) {
        //getChildren().add(der.create().text(title).build());
        setId(title);
        setSpacing(0);
        setStyle("-fx-padding:0; -fx-background-color: white; ");
        Region spring = new Region();
        VBox.setVgrow(spring, Priority.ALWAYS);
        getChildren().addAll(getContent(), spring, getButtons());

        priorButton.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent actionEvent) {
                priorPage();
            }
        });

        nextButton.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent t) {
                nextPage();
            }
        });

        cancelButton.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent t) {
                getWizard().cancel();
            }
        });

        finishButton.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent t) {
                getWizard().finish();
            }
        });
    }

    HBox getButtons() {
        Region spring = new Region();
        HBox.setHgrow(spring, Priority.ALWAYS);
        HBox buttonBar = new HBox(5);
        cancelButton.setCancelButton(true);
        //   finishButton.setDefaultButton(true);
        buttonBar.getChildren().addAll(spring, priorButton, nextButton, cancelButton, finishButton);
        return buttonBar;
    }

    abstract Parent getContent();

    boolean hasNextPage() {
        return getWizard().hasNextPage();
    }

    boolean hasPriorPage() {
        return getWizard().hasPriorPage();
    }

    void nextPage() {
        getWizard().nextPage();
    }

    void priorPage() {
        getWizard().priorPage();
    }

    void navTo(String id) {
        getWizard().navTo(id);
    }

    Wizard getWizard() {
        return (Wizard) getParent();
    }

    public void manageButtons() {
        if (!hasPriorPage()) {
            priorButton.setDisable(true);
        }

        if (!hasNextPage()) {
            nextButton.setDisable(true);
        }
    }

    public void setNewWizard(NewWizard refWizard) {
        newWizardReference = refWizard;
    }
}

/*
 * this Class shows the OFA wizard
 */
class NewWizard extends Wizard {

    String[] splitDeviceDetails;
    TestWizard testWizard;
    Stage owner;
    String topologyDemo, paramFileDemo, ospkFileDemo;
    TreeItem<String> projectExplorerTreeItem;
    OFALoadTree projectNameTree;
    TAI_OFA referenceOFA;
    TAILocale label = new TAILocale(new Locale("en", "EN"));
    String OFAUiPath = label.hierarchyTestON + "/tests/";
    TreeItem<String> treeItem1;
    String paramsFileName, topoFileName;
    boolean flag = false;
    String topologyFileDemo;
    String[] splitDeviceDetail;

    public NewWizard(Stage owner, TreeItem<String> treeItem, TAI_OFA reference, int caseNumber, final ObservableList<TreeItem<String>> listProject1, TreeView<String> projectTree1) {
        super();

        super.setNewWizard(this);

        this.owner = owner;
        testWizard = new TestWizard();

        switch (caseNumber) {
            /*
             * cases --- 
             *     1. New Project
             *     2. New Params file
             *     3. New Topology file
             *     4. New Driver 
             *     
             */
            case 1:
                final ProjectWizard projectWizard = new ProjectWizard();
                ParamsWizard paramsWizard = new ParamsWizard();
                super.setAllData(projectWizard, paramsWizard, new TopologyWizard());
                projectWizard.projectName.textProperty().addListener(new ChangeListener<String>() {
                    @Override
                    public void changed(ObservableValue<? extends String> arg0, String arg1, String arg2) {
                        String message = "\nYour projectName must be\n" + "started with alphabate and \nshould not have special symbol";
                        textValidation("([a-zA-Z]\\d*[a-zA_Z])+|([a-zA-Z]\\d*)+|", arg2, projectWizard.error, projectWizard.nextButton, message, projectWizard.projectName);
                    }
                });
                projectExplorerTreeItem = treeItem;
                referenceOFA = reference;
                paramsWizard.gridPane.add(testWizard.testParams, 0, 0);
                paramsWizard.gridPane.add(new Label(label.wizEmailId), 0, 2);
                paramsWizard.gridPane.add(testWizard.emailId, 1, 2);
                paramsWizard.gridPane.add(new Label("Log Directory "), 0, 3);
                paramsWizard.gridPane.add(testWizard.log_dir, 1, 3);
                paramsWizard.gridPane.add(new Label(label.wizNumberofTestCases), 0, 4);
                paramsWizard.gridPane.add(testWizard.testCases, 1, 4);
                paramsWizard.gridPane.add(testWizard.imageHouse, 60, 0);
                paramsWizard.nextButton.setDisable(false);
                break;

            case 2:

                super.setAllData(testWizard);
                projectExplorerTreeItem = treeItem;
                referenceOFA = reference;
                testWizard.gridPane.add(new Label(label.wizProject), 0, 1);
                testWizard.gridPane.add(testWizard.projectNameList, 1, 1);
                testWizard.gridPane.add(new Label(label.wizParamName), 0, 3);

                testWizard.gridPane.add(testWizard.paramName, 1, 3);

                testWizard.nextButton.setDisable(true);

                testWizard.paramName.textProperty().addListener(new ChangeListener<String>() {
                    @Override
                    public void changed(ObservableValue<? extends String> arg0, String arg1, String arg2) {
                        if (!arg2.isEmpty()) {
                            testWizard.projectNameList.valueProperty().addListener(new ChangeListener() {
                                @Override
                                public void changed(ObservableValue arg0, Object arg1, Object arg2) {
                                    if (!arg2.toString().isEmpty()) {
                                        testWizard.testNameList.valueProperty().addListener(new ChangeListener() {
                                            @Override
                                            public void changed(ObservableValue arg0, Object arg1, Object arg2) {
                                                testWizard.finishButton.setDisable(arg2.toString().isEmpty());
                                            }
                                        });
                                    }
                                }
                            });
                        }
                    }
                });
                Iterator<TreeItem<String>> projectList1 = listProject1.iterator();
                testWizard.projectNameList.getItems().clear();
                while (projectList1.hasNext()) {
                    TreeItem<String> projectComb = projectList1.next();
                    projectComb.getValue();
                    testWizard.projectNameList.getItems().add(projectComb.getValue());
                }

                testWizard.projectNameList.setOnAction(new EventHandler<ActionEvent>() {
                    @Override
                    public void handle(ActionEvent arg0) {

                        final Iterator<TreeItem<String>> projectIterator = listProject1.iterator();
                        while (projectIterator.hasNext()) {
                            final TreeItem<String> treeItem = projectIterator.next();
                            ObservableList<TreeItem<String>> list = treeItem.getChildren();
                            if (treeItem.getValue().equalsIgnoreCase(testWizard.projectNameList.getSelectionModel().getSelectedItem().toString())) {
                                ObservableList<TreeItem<String>> children = treeItem.getChildren();
                                final Iterator<TreeItem<String>> testListIterator = children.iterator();
                                while (testListIterator.hasNext()) {
                                    TreeItem<String> testComb = testListIterator.next();
                                    testComb.getValue();
                                }
                            }
                        }
                    }
                });
                break;

            case 3:
                final ParamsWizard paramWizard = new ParamsWizard();
                super.setAllData(paramWizard, new TopologyWizard());
                projectExplorerTreeItem = treeItem;
                referenceOFA = reference;
                paramWizard.gridPane.add(testWizard.testParams, 0, 0);
                paramWizard.gridPane.add(new Label("Test Name :"), 0, 2);
                paramWizard.gridPane.add(testWizard.projectNameList, 1, 2);
                paramWizard.gridPane.add(new Label("Topology Name"), 0, 3);
                paramWizard.gridPane.add(testWizard.topologyName, 1, 3);
                paramWizard.gridPane.add(testWizard.imageHouse, 60, 0);
                paramWizard.nextButton.setDisable(true);
                Iterator<TreeItem<String>> projectList2 = listProject1.iterator();
                testWizard.projectNameList.getItems().clear();
                while (projectList2.hasNext()) {
                    TreeItem<String> projectComb = projectList2.next();
                    projectComb.getValue();
                    testWizard.projectNameList.getItems().add(projectComb.getValue());
                }

                testWizard.projectNameList.setOnAction(new EventHandler<ActionEvent>() {
                    @Override
                    public void handle(ActionEvent arg0) {

                        final Iterator<TreeItem<String>> projectIterator = listProject1.iterator();
                        while (projectIterator.hasNext()) {
                            final TreeItem<String> treeItem = projectIterator.next();
                            ObservableList<TreeItem<String>> list = treeItem.getChildren();
                            if (treeItem.getValue().equalsIgnoreCase(testWizard.projectNameList.getSelectionModel().getSelectedItem().toString())) {
                                ObservableList<TreeItem<String>> children = treeItem.getChildren();
                                final Iterator<TreeItem<String>> testListIterator = children.iterator();
                                while (testListIterator.hasNext()) {
                                    TreeItem<String> testComb = testListIterator.next();
                                    testComb.getValue();
                                }
                            }
                        }
                    }
                });

                testWizard.topologyName.setOnKeyReleased(new EventHandler<KeyEvent>() {
                    @Override
                    public void handle(KeyEvent t) {
                        if (!testWizard.topologyName.getText().isEmpty()) {
                            paramWizard.nextButton.setDisable(false);
                        } else {
                            paramWizard.nextButton.setDisable(true);
                        }
                    }
                });
                break;
        }
    }

    @Override
    public void finish() {
        String projectName = null;
        String testName = null;
        String testParamsName = null;
        String testTopologyName = null;
        ObservableList<WizardPage> nodeList = super.getAllChildrens();
        int i = 0;

        while (i < nodeList.size()) {
            WizardPage node = nodeList.get(i);
            if (node.getId().equals(label.wizProjectWizardId)) {
                ProjectWizard projectWizard = (ProjectWizard) node;
                projectName = projectWizard.getName();
                new File(OFAUiPath + projectName).mkdir();
                String projectWorkSpacePath = OFAUiPath + projectName;
                File[] file = File.listRoots();
                Path name = new File(projectWorkSpacePath).toPath();
                projectNameTree = new OFALoadTree(name);

                projectExplorerTreeItem.getChildren().add(projectNameTree);
                String pathToFiles = projectNameTree.getFullPath() + "/";


                Path ospkName = new File(projectNameTree.getFullPath() + "/" + projectName + ".ospk").toPath();
                Path paramsName = new File(projectNameTree.getFullPath() + "/" + projectName + ".params").toPath();
                Path topologyName = new File(projectNameTree.getFullPath() + "/" + projectName + ".topo").toPath();

                OFALoadTree topologyTestTree = new OFALoadTree(topologyName);
                topologyTestTree.setValue(topologyName.toString().replace(topologyName.toString(), projectName));

                OFALoadTree ospkTestTree = new OFALoadTree(ospkName);
                ospkTestTree.setValue(ospkName.toString().replace(ospkName.toString(), projectName));

                OFALoadTree paramTestTree = new OFALoadTree(paramsName);
                paramTestTree.setValue(paramsName.toString().replace(paramsName.toString(), projectName));
                projectNameTree.getChildren().addAll(topologyTestTree, paramTestTree, ospkTestTree);

                paramFileDemo = "<PARAMS>" + "\n\t" + "<testcases>  \"1\" </testcases>" + "\n\t"
                        + "<mail> " + testWizard.emailId.getText() + "</mail>\n\t" + "<log_dir>" + testWizard.log_dir.getText() + "</log_dir>" + "\n\n\t"
                        + "<CASE1>" + "\n\t\t" + "#Enter your CASE parameter here in the form" + "\n\t\t" + "#param = value"
                        + "\n\t\t" + "<STEP1>" + "\n\t\t\t" + "#Enter your STEP parameter here in the form" + "\n\t\t\t" + "#param = value" + "\n\t\t" + "</STEP1>" + "\n\t" + "</CASE1>"
                        + "\n" + "\n</PARAMS>";

                ospkFileDemo = "CASE 1" + "\n" + "\t" + "NAME" + " " + "\"Give test case name \"" + "\n" + "\t"
                        + "DESC \"Give test case description\"" + "\n" + "END CASE";

                testTopologyName = projectName + ".topo";
                String topoFileDemo = "<TOPOLOGY>" + "\n\t<COMPONENT>" + "\n\t\t# put components here as given below" + "\n\t\t<component1>" + "\n\t\t\t# put component parameters here"
                        + "\n\t\t  <host> 192.168.56.101 </host>" + "\n\t\t</component1>" + "\n\t</COMPONENT>" + "</TOPOLOGY>";

                try {
                    new File(pathToFiles + "/" + projectName + ".ospk").createNewFile();
                    new File(pathToFiles + "/" + projectName + ".params").createNewFile();
                    new File(pathToFiles + "/" + projectName + ".topo").createNewFile();
                    new File(pathToFiles + "/" + "__init__.py").createNewFile();
                } catch (IOException ex) {
                   
                }
                writeInFile(pathToFiles + "/" + projectName + ".params", paramFileDemo);
                writeInFile(pathToFiles + "/" + projectName + ".ospk", ospkFileDemo);
                
                referenceOFA.checkEditor();
                
            } else if (node.getId().equals(label.wizTestWizardId)) {

                testWizard = (TestWizard) node;
                String selectedProject = testWizard.projectNameList.getSelectionModel().getSelectedItem().toString();
                String paramName = testWizard.paramName.getText();
                String pathParams = "";
                for (int index = 0; index < referenceOFA.projectExplorerTree.getChildren().size(); index++) {

                    if (referenceOFA.projectExplorerTree.getChildren().get(index).getValue().equals(selectedProject)) {

                        pathParams = OFAUiPath + selectedProject;
                        Path name = new File(OFAUiPath + selectedProject + "/" + paramName).toPath();
                        OFALoadTree testSelection = new OFALoadTree(name);

                        Path paramsName = new File(name + ".params").toPath();
                        paramsFileName = paramsName.toString();
                        OFALoadTree paramsTestTree = new OFALoadTree(paramsName);
                        paramsTestTree.setValue(paramName);
                        referenceOFA.projectExplorerTree.getChildren().get(index).getChildren().addAll(paramsTestTree);
                        try {
                            new File(paramsFileName).createNewFile();
                        } catch (IOException ex) {
                            Logger.getLogger(NewWizard.class.getName()).log(Level.SEVERE, null, ex);
                        }
                        writeInFile(paramsFileName, referenceOFA.paramsFileContent);
                    }
                }


            } else if (node.getId().equals(label.wizTopologyWizardId)) {
                TopologyWizard topoWizard = (TopologyWizard) node;

                ArrayList<String> deviceName = new ArrayList<String>();
                Iterator<TextField> attributeIterator = topoWizard.getDeviceNameList().iterator();
                while (attributeIterator.hasNext()) {
                    TextField iteratorAttributeText = attributeIterator.next();
                    deviceName.add(iteratorAttributeText.getText());
                }
                topologyFileDemo = "<TOPOLOGY>" + "\n\t" + "<COMPONENT>" + "\n\t";

                for (String device : topoWizard.getPropertyDetail()) {
                    splitDeviceDetail = device.split("\n");
                    topologyFileDemo += "\n\t\t" + "<" + splitDeviceDetail[0] + ">";
                    splitDeviceDetail = device.split("\n");
                    try {
                        topologyFileDemo += "\n\t\t\t" + "<hostname> " + splitDeviceDetail[1] + "</hostname>\n\t\t\t" + "<user>" + splitDeviceDetail[2]
                                + "</user>\n\t\t\t" + "<password>" + splitDeviceDetail[3] + "</password>\n\t\t\t" + "<type>" + splitDeviceDetail[5] + "</type>\n\t\t\t" + "<coordinate(x,y)>"
                                + splitDeviceDetail[7] + "</coordinate(x,y)>\n\t\t\t";

                        if (topoWizard.topoplogy.testTargetRadioButton.isSelected()) {
                            topologyFileDemo += "<test_target> 1 </test_target>\n\t\t\t" + "<COMPONENTS>";
                        } else {
                            topologyFileDemo += "<COMPONENTS>";
                        }
                        String[] deviceDetailsArray = topoWizard.interFaceValue.toArray(new String[topoWizard.interFaceValue.size()]);
                        int noOfDevices = 0;
                        for (String name : topoWizard.interFaceName) {
                            String propertyDetail = deviceDetailsArray[noOfDevices++];
                            String[] details = propertyDetail.split("\\_");
                            String[] splitInterFace = name.split("\\_");
                            if (splitInterFace[1].equals(splitDeviceDetail[0]) && details[1].equals(splitDeviceDetail[0])) {
                                //              topologyFileDemo +=  "\n\t\t\t"+splitInterFace[0]+"="+details[0];
                            }
                        }
                        for (HashMap<String, String> interFaceDetail : topoWizard.arrayOfInterFaceHash) {
                            Set set = interFaceDetail.entrySet();
                            Iterator interFaceHashDetailIterator = set.iterator();
                            while (interFaceHashDetailIterator.hasNext()) {
                                Map.Entry me = (Map.Entry) interFaceHashDetailIterator.next();
                                String[] deviceNameAndiniterFaceValue = me.getValue().toString().split("\\_");
                                if (deviceNameAndiniterFaceValue[1].equals(splitDeviceDetail[0])) {
                                    if (!me.getKey().toString().isEmpty()) {
                                        if (!me.getKey().toString().equals("//s+")) {
                                            topologyFileDemo += "\n\t\t\t\t" + "<" + me.getKey().toString() + ">" + deviceNameAndiniterFaceValue[0].toString() + "</" + me.getKey().toString() + ">";

                                        }
                                    }
                                }

                            }
                            topologyFileDemo += "\n\t\t\t</COMPONENTS>";
                        }

                        topologyFileDemo += "\n\t\t" + "</" + splitDeviceDetail[0] + ">";

                    } catch (Exception e) {
                    }
                }
                Set set = topoWizard.linkTopologyHash.entrySet();
                Iterator linkHashDetailIterator = set.iterator();
                while (linkHashDetailIterator.hasNext()) {
                    Map.Entry me = (Map.Entry) linkHashDetailIterator.next();

                    String[] linkValue = me.getValue().toString().split("_");
                    String[] linkCoordinates = me.getKey().toString().split("_");

                    topologyFileDemo += "\n\t\t" + "<" + linkValue[0] + ">";
                    topologyFileDemo += "\n\t\t\t" + "<" + linkValue[2].toString() + ">" + linkValue[3].toString() + "</" + linkValue[2].toString() + ">";
                    topologyFileDemo += "\n\t\t\t" + "<" + linkValue[4].toString() + ">" + linkValue[5].toString() + "</" + linkValue[4].toString() + ">";
                    topologyFileDemo += "\n\t\t\t" + "<linkCoordinates(startx,starty,endx,endy)" + ">" + linkCoordinates[1].toString() + "," + linkCoordinates[2] + "," + linkCoordinates[3] + "," + linkCoordinates[4] + "</linkCoordinates(startx,starty,endx,endy)" + ">";
                    topologyFileDemo += "\n\t\t" + "</" + linkValue[0] + ">";

                }

                topologyFileDemo += "\n\t" + "</COMPONENT>" + "\n" + "</TOPOLOGY>";
                String pathTopo = "";
                if (testTopologyName != null) {
                    writeInFile(label.hierarchyTestON + "/tests/" + projectName + "/" + testTopologyName, topologyFileDemo);
                } else {
                    String projectNames = testWizard.projectNameList.getSelectionModel().getSelectedItem().toString();
                    for (int index = 0; index < referenceOFA.projectExplorerTree.getChildren().size(); index++) {

                        if (referenceOFA.projectExplorerTree.getChildren().get(index).getValue().equals(projectNames)) {
                            pathTopo = OFAUiPath + projectNames;
                            Path name = new File(OFAUiPath + projectNames + "/" + testWizard.topologyName.getText()).toPath();
                            OFALoadTree testSelection = new OFALoadTree(name);

                            Path topoName = new File(name + ".topo").toPath();
                            topoFileName = topoName.toString();
                            OFALoadTree topoTestTree = new OFALoadTree(topoName);
                            topoTestTree.setValue(topoFileName);
                            topoTestTree.setValue(topoFileName.toString().replace(topoFileName.toString(), testWizard.topologyName.getText()));

                            referenceOFA.projectExplorerTree.getChildren().get(index).getChildren().addAll(topoTestTree);
                            try {
                                new File(topoFileName).createNewFile();
                            } catch (IOException ex) {
                                Logger.getLogger(NewWizard.class.getName()).log(Level.SEVERE, null, ex);
                            }
                            writeInFile(topoFileName, topologyFileDemo);
                        }
                    }

                }

            }

            i++;
        }
        owner.close();
    }

    public String getParamsFileName() {
        return paramsFileName;
    }

    public void writeInFile(String path, String demoFile) {
        try {
            // Create file 
            FileWriter fstream = new FileWriter(path);
            BufferedWriter out = new BufferedWriter(fstream);
            out.write(demoFile);
            out.close();
        } catch (Exception e) {
            
        }
    }

    public void cancel() {

        owner.close();
    }

    public void textValidation(String regExp, String arg2, Label error, Button nextButton, String text, TextField name) {
        Tooltip tooltip = new Tooltip();
        if (arg2.matches(regExp)) {
            error.setVisible(false);
            nextButton.setDisable(false);
        } else {
            error.setVisible(true);
            nextButton.setDisable(true);
            flag = true;
            String errorImage = "/images/error.png";
            Image saveImage = new Image(getClass().getResourceAsStream(errorImage), 18.0, 18.0, true, true);
            ImageView imageSave = new ImageView(saveImage);
            error.setGraphic(imageSave);

            tooltip.autoFixProperty();
            tooltip.setText(text);
            tooltip.setStyle("-fx-background-color:white");
            error.setTooltip(tooltip);
            Image image = new Image(getClass().getResourceAsStream("/images/error.png"), 24.0, 24.0, true, true);
            tooltip.setGraphic(new ImageView(image));
        }
        if (arg2.isEmpty() || flag == true) {
            nextButton.setDisable(true);
            flag = false;
        }
    }
}

/**
 * This page gathers more information about the new Test
 */
class ProjectWizard extends WizardPage {

    TextField projectName;
    String newProjectName;
    String name;
    boolean flag = false;
    Label error;
    ImageView imageHouse;

    public ProjectWizard() {
        super("Project");

        nextButton.setDisable(true);

        finishButton.setDisable(true);
        this.setId("projectWizard");

    }

    @Override
    Parent getContent() {
        projectName = TextFieldBuilder.create().build();

        projectName.setMinWidth(170);
        nextButton.setDisable(true);
        error = new Label();
        error.setVisible(false);

        error.setTextFill(Color.RED);
        imageHouse = new ImageView(new Image("images/paxterra_logo.jpg", 100, 100, true, true));

        HBox image = new HBox();
        image.setPadding(new Insets(0, 0, 0, 470));
        Button Open = new Button();
        String openImgPath = "/images/TestON.png";
        Open.setStyle("-fx-background-color:white");
        Open.setLayoutX(0);
        Open.setLayoutY(0);
        GridPane gridPane = new GridPane();
        gridPane.setPadding(new Insets(70, 0, 0, 200));
        gridPane.setHgap(10);
        gridPane.setVgap(8);
        Label project = new Label("Project Name");


        gridPane.setId("pane");
        gridPane.add(project, 0, 11);
        gridPane.add(projectName, 1, 11);
        gridPane.add(error, 2, 10);
        gridPane.add(imageHouse, 10, 0);

        return GridPaneBuilder.create().children(gridPane).build();

    }

    void nextPage() {
        // If they have complaints, go to the normal next page

        if (!projectName.getText().equals("")) {
            super.nextPage();
            newProjectName = projectName.getText();

        } else {

            // No complaints? Short-circuit the rest of the pages
            navTo("ParamsWizard");
        }
    }

    public String getName() {
        return newProjectName;
    }
}

/**
 * This page gathers more information about the Test Script
 */
class TestWizard extends WizardPage {

    TextField emailIds;
    TextField numberOfTestCase;
    TextField paramName;
    TextField topologyName;
    String getTestName, getEmailId;
    String getNumberOfTestCases;
    ObservableList<TreeItem<String>> listProject;
    TreeView<String> projectTree;
    ComboBox projectNameList;
    ComboBox testNameList;
    GridPane gridPane;
    Label projectError, testError, emailIdError;
    ImageView imageHouse;
    Text testParams;
    TextField testCases;
    TextField emailId;
    TextField log_dir;
    Text caseParameter;
    Button addParams;

    public TestWizard() {
        super("More Info");
        this.setId("testWizard");
        nextButton.setDisable(true);
        finishButton.setDisable(false);
    }

    @Override
    Parent getContent() {

        HBox image = new HBox();
        image.setPadding(new Insets(0, 0, 0, 470));

        topologyName = TextFieldBuilder.create().build();
        testParams = new Text("Test Params :");
        testParams.setFont(Font.font("Arial", FontWeight.BOLD, 15));
        testParams.setFill(Color.BLUE);
        testCases = TextFieldBuilder.create().build();
        emailId = TextFieldBuilder.create().build();
        log_dir = TextFieldBuilder.create().build();
        caseParameter = new Text("Case Params");
        caseParameter.setFont(Font.font("Arial", FontWeight.BOLD, 10));
        addParams = new Button("Add Case Params");
        projectNameList = ComboBoxBuilder.create().build();
        projectError = new Label();
        projectError.setDisable(true);
        paramName = TextFieldBuilder.create().build();
        imageHouse = new ImageView(new Image("images/TestON.png", 200, 200, true, true));

        testCases.lengthProperty().addListener(new ChangeListener<Number>() {
            @Override
            public void changed(ObservableValue<? extends Number> observable, Number oldValue, Number newValue) {
                if (newValue.intValue() > oldValue.intValue()) {
                    char ch = testCases.getText().charAt(oldValue.intValue());
                    //Check if the new character is the number or other's
                    if (!(ch >= '0' && ch <= '9')) {
                        testCases.setText(testCases.getText().substring(0, testCases.getText().length() - 1));
                    }
                }
            }
        });

        nextButton.setDisable(false);
        finishButton.setDisable(false);
        gridPane = new GridPane();
        gridPane.setPadding(new Insets(30, 0, 0, 40));
        gridPane.setHgap(0);
        gridPane.setVgap(5);
        return GridPaneBuilder.create().children(gridPane).build();
    }

    void nextPage() {

        if (!emailId.getText().equals("") || numberOfTestCase.getText().equals("") || log_dir.getText().equals("")) {
            super.nextPage();

            getEmailId = emailId.getText();
            getNumberOfTestCases = numberOfTestCase.getText();
        } else {

            navTo("topologyWizards");
        }
    }

    public String getTestName() {
        return getTestName;
    }

    public String getEmailId() {
        return getEmailId;
    }

    public String getNumberOfTestCase() {
        return getNumberOfTestCases;
    }
}

/**
 * This page gathers more information about the new Params File
 */
class ParamsWizard extends WizardPage {

    TextField emailIds;
    TextField numberOfTestCase;
    TextField paramName;
    TextField topologyName;
    String getTestName, getEmailId;
    String getNumberOfTestCases;
    ObservableList<TreeItem<String>> listProject;
    TreeView<String> projectTree;
    ComboBox projectNameList;
    ComboBox testNameList;
    GridPane gridPane;
    Label projectError, testError, emailIdError;
    ImageView imageHouse;
    // here is new list
    Text testParams;
    TextField testCases;
    TextField emailId;
    TextField log_dir;
    Text caseParameter;
    Button addParams;
    TextField testTopology;

    public ParamsWizard() {
        super("More Info");
        this.setId("paramsWizard");
        nextButton.setDisable(true);
        finishButton.setDisable(false);
    }

    @Override
    Parent getContent() {

        HBox image = new HBox();
        image.setPadding(new Insets(0, 0, 0, 470));

        testTopology = emailId = TextFieldBuilder.create().build();
        testParams = new Text("Test Params :");
        testParams.setId("testParamsTitle");
        testParams.setFont(Font.font("Arial", FontWeight.BOLD, 15));
        testParams.setFill(Color.BLUE);

        DropShadow dropShadow = new DropShadow();
        dropShadow.setColor(Color.BLACK);
        dropShadow.setRadius(25);
        dropShadow.setSpread(0.25);
        testParams.setEffect(dropShadow);

        testCases = TextFieldBuilder.create().build();
        emailId = TextFieldBuilder.create().build();
        log_dir = TextFieldBuilder.create().build();
        caseParameter = new Text("Case Params");
        caseParameter.setFont(Font.font("Arial", FontWeight.BOLD, 10));
        addParams = new Button("Add Case Params");
        projectNameList = ComboBoxBuilder.create().build();
        projectError = new Label();
        projectError.setDisable(true);
        paramName = TextFieldBuilder.create().build();
        imageHouse = new ImageView(new Image("images/paxterra_logo.jpg", 100, 100, true, true));

        testCases.lengthProperty().addListener(new ChangeListener<Number>() {
            @Override
            public void changed(ObservableValue<? extends Number> observable, Number oldValue, Number newValue) {
                if (newValue.intValue() > oldValue.intValue()) {
                    char ch = testCases.getText().charAt(oldValue.intValue());
                    //Check if the new character is the number or other's
                    if (!(ch >= '0' && ch <= '9')) {
                        testCases.setText(testCases.getText().substring(0, testCases.getText().length() - 1));
                    }
                }
            }
        });
        nextButton.setDisable(false);
        finishButton.setDisable(false);

        gridPane = new GridPane();
        gridPane.setPadding(new Insets(30, 0, 0, 40));
        gridPane.setHgap(0);
        gridPane.setVgap(5);

        return GridPaneBuilder.create().children(gridPane).build();

    }

    void nextPage() {

        if (!emailId.getText().equals("") || testCases.getText().equals("") || log_dir.getText().equals("")) {
            super.nextPage();

            getEmailId = emailId.getText();
            getNumberOfTestCases = testCases.getText();
        } else {

            navTo("topologyWizards");
        }
    }

    public String getTestName() {
        return getTestName;
    }

    public String getEmailId() {
        return getEmailId;
    }

    public String getNumberOfTestCase() {
        return getNumberOfTestCases;
    }
}

/**
 * This page gathers more information about the Test Topology
 */
class TopologyWizard extends WizardPage {

    ArrayList<TextField> deviceNameList = new ArrayList<TextField>();
    ArrayList<String> draggedImagesName = new ArrayList<String>();
    OFATopology topoplogy;
    ArrayList<String> propertyValue = new ArrayList<String>();
    ArrayList<String> interFaceName = new ArrayList<String>();
    ArrayList<String> interFaceValue = new ArrayList<String>();
    TreeView<String> driverExplorerTreeView;
    ArrayList<String> webInfoList = new ArrayList<String>();
    ArrayList<String> webCisco = new ArrayList<String>();
    HashMap<String, String> interFaceHashDetail = new HashMap<String, String>();
    ArrayList<HashMap<String, String>> arrayOfInterFaceHash;
    HashMap<String, String> webToplogyHash = new HashMap<String, String>();
    ArrayList<HashMap<String, String>> arrayOfwebTopologyHash;
    OFATopologyLink topologyLink = new OFATopologyLink();
    HashMap<String, String> linkTopologyHash = new HashMap<String, String>();
    ArrayList<HashMap<String, String>> arrayOfLinkTopologyHash = new ArrayList<HashMap<String, String>>();
    ArrayList<String> topoEditorDeviceInfo = new ArrayList<String>();
    Button lineButtonHorizontal;
    TAILocale label = new TAILocale(new Locale("en", "EN"));
    boolean anchorFlag = false;
    boolean selectFlag = false;

    public TopologyWizard() {
        super("");
        this.setId(label.wizTopologyWizardId);
    }

    Parent getContent() {
        TAILocale label = new TAILocale(Locale.ENGLISH);
        VBox parentTopologyBox = new VBox();
        ToolBar canvasToolBar = new ToolBar();
        lineButtonHorizontal = new Button();

        Tooltip horizontal = new Tooltip("Click to add horizontal line in canvas");
        lineButtonHorizontal.setTooltip(horizontal);
        Image image = new Image(getClass().getResourceAsStream("/images/Link1.png"), 28.0, 28.0, true, true);
        ImageView imageNew = new ImageView(image);
        lineButtonHorizontal.setGraphic(imageNew);

        Button lineButtonVertical = new Button();
        Tooltip vertical = new Tooltip("Click to add vertical line in canvas");
        lineButtonVertical.setTooltip(vertical);

        final Button deleteAllButton = new Button();
        Tooltip delete = new Tooltip("Click to reset or clear canvas");
        deleteAllButton.setTooltip(delete);
        Image image2 = new Image(getClass().getResourceAsStream("/images/Refresh.png"), 24.0, 24.0, true, true);
        ImageView imageNew2 = new ImageView(image2);
        deleteAllButton.setGraphic(imageNew2);

        Image image1 = new Image(getClass().getResourceAsStream("/images/verticalLine.jpg"), 24.0, 24.0, true, true);
        ImageView imageNew1 = new ImageView(image1);
        lineButtonVertical.setGraphic(imageNew1);

        canvasToolBar.getItems().addAll(lineButtonHorizontal, deleteAllButton);
        HBox topologyBox = new HBox();
        TabPane topologyPane = new TabPane();
        topologyPane.setSide(Side.LEFT);
        final Tab topologyModifiedDriverExplorerTab = new Tab("DEVICES");
        topologyPane.setMaxWidth(250);

        String hostName = label.hierarchyTestON + "/drivers/common";
        final Node rootIcon = new ImageView(new Image(getClass().getResourceAsStream("/images/project.jpeg"), 16, 16, true, true));
        TreeItem<String> driverExplorerTree = new TreeItem<String>("Drivers");
        File[] file = File.listRoots();
        Path name = new File(hostName).toPath();
        LoadDirectory treeNode = new LoadDirectory(name);
        driverExplorerTree = treeNode;
        driverExplorerTree.setExpanded(true);
        driverExplorerTreeView = new TreeView<String>(driverExplorerTree);
        topologyModifiedDriverExplorerTab.setContent(driverExplorerTreeView);
        driverExplorerTreeView.setShowRoot(false);
        topologyPane.getTabs().add(topologyModifiedDriverExplorerTab);
        topologyModifiedDriverExplorerTab.setClosable(false);

        final TabPane topologyNewCanvas = new TabPane();
        topologyNewCanvas.setSide(Side.BOTTOM);
        final Tab canvasTab = new Tab("Canvas");
        canvasTab.setClosable(false);
        Button mew = new Button("CLICK");
        mew.setGraphic(rootIcon);
        HBox hBox1 = new HBox();
        hBox1.setPrefWidth(345);
        hBox1.setPrefHeight(200);
        hBox1.setStyle("-fx-border-color: blue;"
                + "-fx-border-width: 1;"
                + "-fx-border-style: solid;");
        Pane box1 = new Pane();
        box1.setPrefWidth(500);
        box1.setPrefHeight(200);
        canvasTab.setContent(box1);
        topologyNewCanvas.getTabs().add(canvasTab);
        deleteAllButton.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent arg0) {
                Pane pane = (Pane) canvasTab.getContent();
                ObservableList<Node> list = pane.getChildren();
                pane.getChildren().removeAll(list);

            }
        });
        lineButtonVertical.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent arg0) {
                final Line connecting = new Line();
                connecting.setStrokeWidth(3);
                connecting.setEndY(90);
                connecting.setLayoutX(33);
                connecting.setLayoutY(33);

                final DraggableNode contentLine = new DraggableNode();
                contentLine.setOnMouseClicked(new EventHandler<MouseEvent>() {
                    @Override
                    public void handle(MouseEvent arg0) {
                        if (arg0.getClickCount() == 2) {
                            OFATopologyLink topologyLink = new OFATopologyLink();
                            topologyLink.start(new Stage());
                        } else if (arg0.getButton() == MouseButton.SECONDARY) {
                            deleteLineContextMenu(contentLine, connecting, arg0);
                        }
                    }
                });

                contentLine.getChildren().add(connecting);

                Pane created = (Pane) canvasTab.getContent();

                created.getChildren().addAll(contentLine);
            }
        });

        driverExplorerTreeView.setOnDragDetected(new EventHandler<MouseEvent>() {
            @Override
            public void handle(MouseEvent arg0) {
                final MultipleSelectionModel<TreeItem<String>> selectedItem = driverExplorerTreeView.getSelectionModel();
                try {
                    Image i = new Image(selectedItem.getSelectedItem().getGraphic().getId(), 60, 60, true, true);
                    Dragboard db = driverExplorerTreeView.startDragAndDrop(TransferMode.COPY);

                    ClipboardContent content = new ClipboardContent();
                    content.putImage(i);
                    db.setContent(content);

                    arg0.consume();
                } catch (Exception e) {
                }

            }
        });

        final Pane pane = (Pane) canvasTab.getContent();
        pane.setOnDragOver(new EventHandler<DragEvent>() {
            @Override
            public void handle(DragEvent t) {

                Dragboard db = t.getDragboard();

                if (db.hasImage()) {
                    t.acceptTransferModes(TransferMode.COPY);
                }
                t.consume();
            }
        });

        pane.setOnDragDropped(new EventHandler<DragEvent>() {
            @Override
            public void handle(DragEvent event) {

                Dragboard db = event.getDragboard();

                if (db.hasImage()) {

                    insertImage(db.getImage(), pane, event.getX(), event.getY());

                    event.setDropCompleted(true);
                } else {
                    event.setDropCompleted(false);
                }
                event.consume();
            }
        });

        SingleSelectionModel<Tab> tab = topologyNewCanvas.getSelectionModel();
        tab.getSelectedItem().getContent().setOnMouseClicked(new EventHandler<MouseEvent>() {
            @Override
            public void handle(MouseEvent arg0) {
                SingleSelectionModel<Tab> tab1 = topologyNewCanvas.getSelectionModel();
            }
        });

        topologyBox.getChildren().addAll(topologyPane, topologyNewCanvas);
        parentTopologyBox.getChildren().addAll(canvasToolBar, topologyBox);
        return parentTopologyBox;
    }

    void insertImage(Image i, final Pane hb, double x, double y) {
        final TextField text = new TextField();
        final String[] deviceInfo;;
        text.setId(driverExplorerTreeView.getSelectionModel().getSelectedItem().getValue().toString() + "_" + driverExplorerTreeView.getSelectionModel().getSelectedItem().getParent().getValue());
        deviceInfo = text.getId().split("\\_");
        deviceNameList.add(text);
        text.setPrefWidth(100);
        ImageView iv = new ImageView();
        iv.setImage(i);

        final DraggableNode content = new DraggableNode();
        final VBox hbox = new VBox();
        hbox.setPrefWidth(80);
        hbox.setPrefHeight(100);
        lineButtonHorizontal.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent arg0) {
                final Line connecting = new Line(33, 43, 33, 43);
                connecting.setId("Line");
                connecting.setStrokeLineCap(StrokeLineCap.ROUND);
                connecting.setStroke(Color.MIDNIGHTBLUE);
                connecting.setStrokeWidth(2.5);
                final TopologyWizard.Anchor anchor1 = new TopologyWizard.Anchor("Anchor 1", connecting.startXProperty(), connecting.startYProperty());
                final TopologyWizard.Anchor anchor2 = new TopologyWizard.Anchor("Anchor 2", connecting.endXProperty(), connecting.endYProperty());
                anchor1.setFill(Color.TRANSPARENT.deriveColor(1, 1, 1, 0.5));
                anchor2.setFill(Color.TRANSPARENT.deriveColor(1, 1, 1, 0.5));
                Circle[] circles = {anchor1, anchor2};
                for (Circle circle : circles) {
                    enableDrag(circle);
                }
                enableDragLineWithAnchors(connecting, anchor1, anchor2);

                anchor1.setOnMouseEntered(new EventHandler<MouseEvent>() {
                    @Override
                    public void handle(MouseEvent arg0) {
                        anchor1.setFill(Color.GOLD.deriveColor(1, 1, 1, 0.5));
                        anchor1.setVisible(true);
                        anchor2.setVisible(true);
                    }
                });

                anchor1.setOnMouseExited(new EventHandler<MouseEvent>() {
                    @Override
                    public void handle(MouseEvent arg0) {
                        anchor1.setFill(Color.TRANSPARENT.deriveColor(1, 1, 1, 0.5));
                        anchor1.setVisible(false);
                        anchor2.setVisible(false);
                    }
                });

                anchor2.setOnMouseEntered(new EventHandler<MouseEvent>() {
                    @Override
                    public void handle(MouseEvent arg0) {
                        anchor2.setFill(Color.GOLD.deriveColor(1, 1, 1, 0.5));
                        anchor1.setVisible(true);
                        anchor2.setVisible(true);
                    }
                });

                anchor2.setOnMouseExited(new EventHandler<MouseEvent>() {
                    @Override
                    public void handle(MouseEvent arg0) {
                        anchor2.setFill(Color.TRANSPARENT.deriveColor(1, 1, 1, 0.5));
                        anchor1.setVisible(false);
                        anchor2.setVisible(false);
                    }
                });

                connecting.setOnMouseEntered(new EventHandler<MouseEvent>() {
                    @Override
                    public void handle(MouseEvent arg0) {
                        connecting.setStroke(Color.GOLD);
                        anchor1.setVisible(true);
                        anchor2.setVisible(true);
                    }
                });
                connecting.setOnMouseExited(new EventHandler<MouseEvent>() {
                    @Override
                    public void handle(MouseEvent arg0) {
                        connecting.setStroke(Color.MIDNIGHTBLUE);
                        anchor1.setVisible(false);
                        anchor2.setVisible(false);

                    }
                });

                final DraggableNode contentLine = new DraggableNode();

                connecting.setOnMouseClicked(new EventHandler<MouseEvent>() {
                    @Override
                    public void handle(MouseEvent arg0) {
                        if (arg0.getClickCount() == 2) {

                            topologyLink.start(new Stage());

                            if (arrayOfLinkTopologyHash.isEmpty()) {
                                for (HashMap<String, String> linkHash : arrayOfLinkTopologyHash) {
                                    Set linkSet = linkHash.entrySet();
                                    Iterator linkHashDetailIterator = linkSet.iterator();
                                    while (linkHashDetailIterator.hasNext()) {

                                        Map.Entry linkMap = (Map.Entry) linkHashDetailIterator.next();

                                        if (linkMap.getKey().toString().equals(connecting.getId())) {
                                            String[] linkValues = linkMap.getValue().toString().split("_");

                                            topologyLink.nameText.setText(linkValues[0]);
                                            topologyLink.typeText.setText(linkValues[1]);
                                            topologyLink.devicesInTopoEditor.setEditable(true);
                                            topologyLink.devicesInTopoEditor.getSelectionModel().select(linkValues[2]);
                                            topologyLink.interfaceList2.setEditable(true);
                                            topologyLink.interfaceList2.getSelectionModel().select(linkValues[3]);
                                            topologyLink.destDevicesInTopoEditor.setEditable(true);
                                            topologyLink.destDevicesInTopoEditor.getSelectionModel().select(linkValues[4]);
                                            topologyLink.interfaceList4.setEditable(true);
                                            topologyLink.interfaceList4.getSelectionModel().select(linkValues[5]);

                                        }
                                    }
                                }
                            }

                            for (String string : draggedImagesName) {
                                topologyLink.devicesInTopoEditor.getItems().add(string);
                                topologyLink.destDevicesInTopoEditor.getItems().add(string);
                            }

                            topologyLink.devicesInTopoEditor.setOnAction(new EventHandler<ActionEvent>() {
                                @Override
                                public void handle(ActionEvent arg0) {
                                    topologyLink.interfaceList2.getItems().clear();
                                    try {
                                        for (HashMap<String, String> interFaceDetail : arrayOfInterFaceHash) {
                                            Set set = interFaceDetail.entrySet();
                                            Iterator interFaceHashDetailIterator = set.iterator();
                                            while (interFaceHashDetailIterator.hasNext()) {
                                                Map.Entry me = (Map.Entry) interFaceHashDetailIterator.next();

                                                String[] deviceNameAndiniterFaceValue = me.getValue().toString().split("\\_");

                                                if (deviceNameAndiniterFaceValue[1].equals(topologyLink.devicesInTopoEditor.getSelectionModel().getSelectedItem())) {
                                                    if (!me.getKey().toString().equals("")) {
                                                        topologyLink.interfaceList2.getItems().add(me.getKey().toString());

                                                    }
                                                }

                                            }
                                        }
                                    } catch (Exception e) {
                                    }
                                }
                            });

                            topologyLink.destDevicesInTopoEditor.setOnAction(new EventHandler<ActionEvent>() {
                                @Override
                                public void handle(ActionEvent arg0) {
                                    topologyLink.interfaceList4.getItems().clear();
                                    try {
                                        for (HashMap<String, String> interFaceDetail : arrayOfInterFaceHash) {
                                            Set set = interFaceDetail.entrySet();
                                            Iterator interFaceHashDetailIterator = set.iterator();
                                            while (interFaceHashDetailIterator.hasNext()) {
                                                Map.Entry me = (Map.Entry) interFaceHashDetailIterator.next();
                                                String[] deviceNameAndiniterFaceValue = me.getValue().toString().split("\\_");
                                                if (deviceNameAndiniterFaceValue[1].equals(topologyLink.destDevicesInTopoEditor.getSelectionModel().getSelectedItem())) {
                                                    if (!me.getKey().toString().equals("")) {
                                                        topologyLink.interfaceList4.getItems().add(me.getKey().toString());
                                                    }
                                                }
                                            }
                                        }
                                    } catch (Exception e) {
                                    }
                                }
                            });

                            topologyLink.finishSelectedLink.setOnAction(new EventHandler<ActionEvent>() {
                                @Override
                                public void handle(ActionEvent arg0) {
                                    connecting.setId(topologyLink.nameText.getText() + "_" + connecting.getStartX() + "_" + connecting.getStartY() + "_" + connecting.getEndX() + "_" + connecting.getEndY());
                                    String detailedString = topologyLink.nameText.getText() + "_" + topologyLink.typeText.getText() + "_" + topologyLink.devicesInTopoEditor.getSelectionModel().getSelectedItem() + "_" + topologyLink.interfaceList2.getSelectionModel().getSelectedItem() + "_" + topologyLink.destDevicesInTopoEditor.getSelectionModel().getSelectedItem() + "_" + topologyLink.interfaceList4.getSelectionModel().getSelectedItem() + "_";
                                    linkTopologyHash.put(connecting.getId(), detailedString);
                                    arrayOfLinkTopologyHash = new ArrayList<HashMap<String, String>>();
                                    arrayOfLinkTopologyHash.add(linkTopologyHash);
                                    topologyLink.copyStage.close();
                                }
                            });
                        } else if (arg0.getButton() == MouseButton.SECONDARY) {
                            deleteLineContextMenu(contentLine, connecting, arg0);
                        }
                    }
                });
                hb.getChildren().addAll(connecting, anchor1, anchor2);
            }
        });

        content.setOnMouseClicked(new EventHandler<MouseEvent>() {
            @Override
            public void handle(MouseEvent arg0) {
                if (anchorFlag == false) {
                    if (arg0.getClickCount() == 1) {
                        final Line con = new Line();
                        con.setStrokeLineCap(StrokeLineCap.ROUND);
                        con.setStroke(Color.MIDNIGHTBLUE);
                        con.setStrokeWidth(2.0);

                        final Line con1 = new Line();
                        con1.setStrokeLineCap(StrokeLineCap.ROUND);
                        con1.setStroke(Color.MIDNIGHTBLUE);
                        con1.setStrokeWidth(2.0);

                        final Line con2 = new Line();
                        con2.setStrokeLineCap(StrokeLineCap.ROUND);
                        con2.setStroke(Color.MIDNIGHTBLUE);
                        con2.setStrokeWidth(2.0);

                        final Line con3 = new Line();
                        con3.setStrokeLineCap(StrokeLineCap.ROUND);
                        con3.setStroke(Color.MIDNIGHTBLUE);
                        con3.setStrokeWidth(2.0);

                        OFAAnchorInsideImageNode mainAnchor = new OFAAnchorInsideImageNode(226.0, 41.0);
                        final Anchor anchor3 = new Anchor("anchor3", con.startXProperty(), con.startYProperty());
                        final Anchor anchor4 = new Anchor("anchor4", con.endXProperty(), con.endYProperty());
                        final Anchor anchor5 = new Anchor("anchor5", con1.startXProperty(), con1.startYProperty());
                        final Anchor anchor6 = new Anchor("anchor6", con1.endXProperty(), con1.endYProperty());
                        final Anchor anchor7 = new Anchor("anchor7", con2.startXProperty(), con2.startYProperty());
                        final Anchor anchor8 = new Anchor("anchor8", con2.endXProperty(), con2.endYProperty());
                        final Anchor anchor9 = new Anchor("anchor9", con3.startXProperty(), con3.startYProperty());
                        final Anchor anchor10 = new Anchor("anchor10", con3.endXProperty(), con3.endYProperty());
                        anchor3.setLayoutX(content.getLayoutX());
                        anchor3.setLayoutY(content.getLayoutY());
                        anchor3.setVisible(false);
                        anchor4.setLayoutX(content.getLayoutX() + 40);
                        anchor4.setLayoutY(content.getLayoutY());
                        anchor5.setLayoutX(content.getLayoutX());
                        anchor5.setLayoutY(content.getLayoutY());
                        anchor5.setVisible(false);
                        anchor6.setLayoutX(content.getLayoutX() + 40);
                        anchor6.setLayoutY(content.getLayoutY() + 100);
                        anchor7.setLayoutX(content.getLayoutX());
                        anchor7.setLayoutY(content.getLayoutY());
                        anchor7.setVisible(false);
                        anchor8.setLayoutX(content.getLayoutX());
                        anchor8.setLayoutY(content.getLayoutY() + 50);
                        anchor9.setLayoutX(content.getLayoutX());
                        anchor9.setLayoutY(content.getLayoutY());
                        anchor9.setVisible(false);
                        anchor10.setLayoutX(content.getLayoutX() + 80);
                        anchor10.setLayoutY(content.getLayoutY() + 50);

                        con1.setLayoutX(anchor6.getLayoutX());
                        con1.setLayoutY(anchor6.getLayoutY());
                        con.setLayoutX(anchor4.getLayoutX());
                        con.setLayoutY(anchor4.getLayoutY());
                        con2.setLayoutX(anchor8.getLayoutX());
                        con2.setLayoutY(anchor8.getLayoutY());
                        con3.setLayoutX(anchor10.getLayoutX());
                        con3.setLayoutY(anchor10.getLayoutY());

                        con.setId("connectingLine");
                        con.setLayoutX(anchor4.getLayoutX());
                        con.setLayoutY(anchor4.getLayoutY());

                        anchorFlag = true;
                        hb.getChildren().addAll(con, anchor3, anchor4, con1, anchor5, anchor6, con2, anchor7, anchor8, con3, anchor9, anchor10);
                        HashMap<Node, String> anchorNodeHash = new HashMap();

                        anchorNodeHash.put(anchor4, anchor4.getId());
                        anchorNodeHash.put(anchor6, anchor6.getId());
                        anchorNodeHash.put(anchor8, anchor8.getId());
                        anchorNodeHash.put(anchor10, anchor10.getId());
                        anchorNodeHash.put(con1, con1.getId());
                        anchorNodeHash.put(con2, con2.getId());
                        anchorNodeHash.put(con3, con3.getId());
                        anchorNodeHash.put(con, con.getId());

                        final ObservableList<Node> allNodeInCanvas = hb.getChildren();
                        mainAnchor.anchorsInsideImage(anchor4, 40, 0, 40, 100, hb, content, hbox, con, draggedImagesName, arrayOfInterFaceHash, linkTopologyHash, anchorNodeHash);
                        mainAnchor.anchorsInsideImage(anchor6, 40, 100, 40, 0, hb, content, hbox, con, draggedImagesName, arrayOfInterFaceHash, linkTopologyHash, anchorNodeHash);
                        mainAnchor.anchorsInsideImage(anchor8, 0, 50, 80, 50, hb, content, hbox, con, draggedImagesName, arrayOfInterFaceHash, linkTopologyHash, anchorNodeHash);
                        mainAnchor.anchorsInsideImage(anchor10, 80, 50, 0, 50, hb, content, hbox, con, draggedImagesName, arrayOfInterFaceHash, linkTopologyHash, anchorNodeHash);

                        hbox.setOnDragDetected(new EventHandler<MouseEvent>() {
                            @Override
                            public void handle(MouseEvent t) {
                                hbox.startFullDrag();
                            }
                        });

                        hbox.setOnMouseDragged(new EventHandler<MouseEvent>() {
                            @Override
                            public void handle(MouseEvent t) {
                                anchorFlag = false;
                                hb.getChildren().removeAll(con, con1, con2, con3, anchor4, anchor6, anchor8, anchor10);
                            }
                        });

                        content.setOnMouseMoved(new EventHandler<MouseEvent>() {
                            @Override
                            public void handle(MouseEvent arg0) {
                                Double x13 = content.getScene().getX() + 482.0 + 53.0;
                                Double x14 = content.getLayoutX() + 482.0;
                                Double y13 = content.getScene().getY() + 142.0 + 92.0;
                                Double y14 = content.getLayoutY() + 142.0;
                                boolean exitFlag = false;
                                for (int i = 0; i <= 80; i++) {
                                    for (int j = 0; j <= 100; j++) {
                                        Double x1 = content.getScene().getX();
                                        Double y1 = content.getScene().getX();
                                        Double x11 = x1 + i;
                                        Double y11 = y1 + j;
                                        if (x11 == arg0.getSceneX()) {
                                            if (y11 == arg0.getSceneY()) {
                                                exitFlag = true;
                                            }
                                        }
                                    }
                                }

                                if (exitFlag == false) {
                                    anchorFlag = false;
                                    hb.getChildren().removeAll(con, con1, con2, con3, anchor4, anchor5, anchor6, anchor7, anchor8, anchor9, anchor10);
                                }
                            }
                        });

                    }
                }

                if (arg0.getClickCount() == 2) {
                    if (deviceInfo[0].equals("fvtapidriver") || deviceInfo[0].equals("poxclidriver") || deviceInfo[0].equals("mininetclidriver") || deviceInfo[0].equals("dpctlclidriver")
                            || deviceInfo[0].equals("floodlightclidriver") || deviceInfo[0].equals("flowvisorclidriver") || deviceInfo[0].equals("hpswitchclidriver")
                            || deviceInfo[0].equals("remotevmdriver") || deviceInfo[0].equals("remotepoxdriver") || deviceInfo[0].equals("flowvisordriver") || deviceInfo[0].equals("switchclidriver")) {
                        try {
                            topoplogy = new OFATopology();
                            topoplogy.start(new Stage());
                        } catch (Exception ex) {
                            Logger.getLogger(TopologyWizard.class.getName()).log(Level.SEVERE, null, ex);
                        }

                        if (topoplogy.testTargetRadioButton.isSelected()) {
                            selectFlag = true;
                        }

                        topoplogy.cancelButton.setOnAction(new EventHandler<ActionEvent>() {
                            @Override
                            public void handle(ActionEvent arg0) {
                                topoplogy.copyStage.close();
                            }
                        });
                        
                        topoplogy.save.setOnAction(new EventHandler<ActionEvent>() {
                            @Override
                            public void handle(ActionEvent arg0) {
                                topoplogy.getHostName = topoplogy.hostNameText.getText();
                                topoplogy.getUserName = topoplogy.userNameText.getText();
                                topoplogy.getPassword = topoplogy.passwordText.getText();

                                for (int i = 0; i < topoplogy.deviceTable.getItems().size(); i++) {
                                    topoplogy.deviceTable.getSelectionModel().select(i);
                                    interFaceHashDetail.put(topoplogy.deviceTable.getSelectionModel().getSelectedItem().getDeviceName().getText(), topoplogy.deviceTable.getSelectionModel().getSelectedItem().getDeviceType().getText() + "_" + text.getText());
                                    arrayOfInterFaceHash = new ArrayList<HashMap<String, String>>();
                                    arrayOfInterFaceHash.add(interFaceHashDetail);
                                }

                                draggedImagesName.add(text.getText());
                                propertyValue.add(text.getText() + "\n" + topoplogy.getHostName + "\n" + topoplogy.getUserName + "\n" + topoplogy.getPassword + "\n" + topoplogy.getTranportProtocol + "\n" + deviceInfo[0] + "\n" + topoplogy.getPort + "\n" + content.getId());
                                topoplogy.copyStage.close();
                            }
                        });
                    }
                    if (deviceInfo[1].equals("cli") || deviceInfo[1].equals("poxclidriver") || deviceInfo[1].equals("mininetclidriver") || deviceInfo[1].equals("dpctlclidriver")
                            || deviceInfo[1].equals("floodlightclidriver") || deviceInfo[1].equals("flowvisorclidriver") || deviceInfo[1].equals("hpswitchclidriver")
                            || deviceInfo[1].equals("remotevmdriver") || deviceInfo[1].equals("remotepoxdriver") || deviceInfo[1].equals("flowvisordriver") || deviceInfo[1].equals("switchclidriver")) {
                        try {
                            topoplogy = new OFATopology();
                            topoplogy.start(new Stage());
                        } catch (Exception ex) {
                            Logger.getLogger(TopologyWizard.class.getName()).log(Level.SEVERE, null, ex);
                        }

                        topoplogy.cancelButton.setOnAction(new EventHandler<ActionEvent>() {
                            @Override
                            public void handle(ActionEvent arg0) {
                                topoplogy.copyStage.close();
                            }
                        });
                    
                        try {
                            topoplogy.save.setOnAction(new EventHandler<ActionEvent>() {
                                @Override
                                public void handle(ActionEvent arg0) {
                                    topoplogy.getHostName = topoplogy.hostNameText.getText();
                                    topoplogy.getUserName = topoplogy.userNameText.getText();
                                    topoplogy.getPassword = topoplogy.passwordText.getText();
                                    for (int i = 0; i < topoplogy.deviceTable.getItems().size(); i++) {
                                        topoplogy.deviceTable.getSelectionModel().select(i);
                                        interFaceHashDetail.put(topoplogy.deviceTable.getSelectionModel().getSelectedItem().getDeviceName().getText(), topoplogy.deviceTable.getSelectionModel().getSelectedItem().getDeviceType().getText() + "_" + text.getText());
                                        arrayOfInterFaceHash = new ArrayList<HashMap<String, String>>();
                                        arrayOfInterFaceHash.add(interFaceHashDetail);
                                    }
                                    draggedImagesName.add(text.getText());
                                    propertyValue.add(text.getText() + "\n" + topoplogy.getHostName + "\n" + topoplogy.getUserName + "\n" + topoplogy.getPassword + "\n" + topoplogy.getTranportProtocol + "\n" + deviceInfo[0] + "\n" + topoplogy.getPort + "\n" + content.getId());
                                    topoplogy.copyStage.close();
                                }
                            });
                        } catch (Exception e) {
                        }
                    }

                }
            }
        });

        final Button closeButton = new Button();
        Tooltip close = new Tooltip();
        close.setText("Delete this device");
        closeButton.setTooltip(close);
        Image image = new Image(getClass().getResourceAsStream("/images/close_icon2.jpg"), 12, 12, true, true);
        ImageView imageNew3 = new ImageView(image);
        closeButton.setGraphic(imageNew3);
        closeButton.setStyle("-fx-background-color: white;");

        final ArrayList<Node> removeNodes = new ArrayList<Node>();
        closeButton.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent arg0) {
                OFAAnchorInsideImageNode node = new OFAAnchorInsideImageNode(224.0, 41.0);
                node.closeNodeOnCanvas(closeButton, hbox, hb, content);
                Node parent = hbox.getParent();
                ObservableList<Node> allCurrentNode = hb.getChildren();
                for (Node node1 : allCurrentNode) {
                    if (node1.toString().contains("Line")) {
                        if (!node1.toString().matches("Line[id=Line[id=null,null]]")) {
                            if (node1.getId() != null) {
                                String[] startLineNode = node1.getId().split(",");
                                Integer nodeHash = content.hashCode();

                                if (nodeHash.toString().equals(startLineNode[0])) {
                                    removeNodes.add(node1);
                                }

                                if (startLineNode.length == 2) {
                                    if (nodeHash.toString().equals(startLineNode[1])) {
                                        removeNodes.add(node1);
                                    }
                                }
                            }
                        }
                    }
                }

                for (Node removenode : removeNodes) {
                    hb.getChildren().remove(removenode);
                }

                hb.getChildren().remove(content);

            }
        });

        hbox.getChildren().addAll(closeButton, iv, text);
        hbox.setId(iv.toString());

        text.setPromptText("Device Name");
        content.getChildren().add(hbox);

        content.setOnMouseEntered(new EventHandler<MouseEvent>() {
            @Override
            public void handle(MouseEvent arg0) {
                hbox.setStyle("-fx-border-color: Gold");
            }
        });

        content.setOnMouseExited(new EventHandler<MouseEvent>() {
            @Override
            public void handle(MouseEvent arg0) {
                hbox.setStyle("-fx-border-color: Transparent");
                Double xcoordinate = content.getLayoutX();
                Double ycoordinate = content.getLayoutY();
                OFATopology device = new OFATopology();

                content.setId(xcoordinate.toString() + "," + ycoordinate.toString());
            }
        });

        content.setLayoutX(x - 40);
        content.setLayoutY(y - 30);
        hb.getChildren().add(content);
    }

    void anchorsInsideImageNode(final Anchor anchor, final double bindLinex, final double bindLiney, final Pane hb, final DraggableNode content, final VBox hbox, final Line con) {


        final Line con11 = new Line();

        anchor.setOnDragDetected(new EventHandler<MouseEvent>() {
            @Override
            public void handle(MouseEvent arg0) {
                anchor.startFullDrag();
                enableDrag(anchor);
            }
        });

        anchor.setOnMouseExited(new EventHandler<MouseEvent>() {
            @Override
            public void handle(MouseEvent arg0) {

                boolean exitFlag = false;
                for (int i = 0; i <= 80; i++) {
                    for (int j = 0; j <= 100; j++) {
                        Double x1 = anchor.getLayoutX() + 482.0;
                        Double y1 = anchor.getLayoutY() + 142.0;
                        Double x11 = x1 + i;
                        Double y11 = y1 + j;
                        if (x11 == arg0.getSceneX()) {
                            if (y11 == arg0.getSceneY()) {
                                exitFlag = true;

                            }
                        }
                    }
                }
                if (exitFlag == false) {
                    hbox.setStyle("-fx-border-color: Transparent");
                    anchor.setVisible(false);
                    con.setVisible(false);

                }
            }
        });

        hbox.setOnMouseDragged(new EventHandler<MouseEvent>() {
            @Override
            public void handle(MouseEvent arg0) {
                try {
                    con.setVisible(false);
                    anchor.setVisible(false);
                    hb.getChildren().removeAll(con, anchor);
                } catch (Exception e) {
                }

            }
        });

        anchor.setOnMouseDragReleased(new EventHandler<MouseDragEvent>() {
            @Override
            public void handle(MouseDragEvent arg0) {

                ObservableList<Node> allNodesCanvas = hb.getChildren();
                boolean flag = false;
                try {
                    for (Node node : allNodesCanvas) {

                        Double x = node.getLayoutX() + 226.0;
                        Double y = node.getLayoutY() + 41.0;

                        if (node.toString().startsWith("DraggableNode")) {
                            for (int i = 0; i <= 80; i++) {
                                for (int j = 0; j <= 100; j++) {
                                    Double x1 = node.getLayoutX() + 226.0;
                                    Double y1 = node.getLayoutY() + 41.0;
                                    Double x11 = x1 + i;
                                    Double y11 = y1 + j;
                                    if (x11 == arg0.getSceneX()) {
                                        if (y11 == arg0.getSceneY()) {
                                            con11.setStrokeLineCap(StrokeLineCap.ROUND);
                                            con11.setStroke(Color.MIDNIGHTBLUE);
                                            con11.setStrokeWidth(2.0);
                                            con11.startXProperty().bind(content.layoutXProperty().add(bindLinex));
                                            con11.startYProperty().bind(content.layoutYProperty().add(bindLiney));
                                            con11.endXProperty().bind(node.layoutXProperty().add(bindLinex));
                                            con11.endYProperty().bind(node.layoutYProperty().add(bindLiney));

                                            hbox.setStyle("-fx-border-color: Transparent");

                                            hb.getChildren().add(con11);
                                            con.setVisible(false);
                                            anchor.setVisible(false);
                                            flag = true;

                                        }

                                    }
                                }
                            }

                        }

                    }
                    if (flag == false) {
                        con.setVisible(false);
                        anchor.setVisible(false);
                    }
                } catch (Exception e) {
                    
                }

            }
        });

        con11.setOnMouseEntered(new EventHandler<MouseEvent>() {
            @Override
            public void handle(MouseEvent arg0) {

                con11.setStroke(Color.GOLD);

            }
        });
        con11.setOnMouseExited(new EventHandler<MouseEvent>() {
            @Override
            public void handle(MouseEvent arg0) {

                con11.setStroke(Color.MIDNIGHTBLUE);
            }
        });

        final DraggableNode contentLine = new DraggableNode();
        con11.setOnMouseClicked(new EventHandler<MouseEvent>() {
            @Override
            public void handle(MouseEvent arg0) {
                if (arg0.getClickCount() == 2) {

                    topologyLink.start(new Stage());

                    if (arrayOfLinkTopologyHash.isEmpty()) {
                        for (HashMap<String, String> linkHash : arrayOfLinkTopologyHash) {
                            Set linkSet = linkHash.entrySet();
                            Iterator linkHashDetailIterator = linkSet.iterator();
                            while (linkHashDetailIterator.hasNext()) {

                                Map.Entry linkMap = (Map.Entry) linkHashDetailIterator.next();
                                if (linkMap.getKey().toString().equals(con11.getId())) {
                                    String[] linkValues = linkMap.getValue().toString().split("_");
                                    topologyLink.nameText.setText(linkValues[0]);
                                    topologyLink.typeText.setText(linkValues[1]);
                                    topologyLink.devicesInTopoEditor.setEditable(true);
                                    topologyLink.devicesInTopoEditor.getSelectionModel().select(linkValues[2]);
                                    topologyLink.interfaceList2.setEditable(true);
                                    topologyLink.interfaceList2.getSelectionModel().select(linkValues[3]);
                                    topologyLink.destDevicesInTopoEditor.setEditable(true);
                                    topologyLink.destDevicesInTopoEditor.getSelectionModel().select(linkValues[4]);
                                    topologyLink.interfaceList4.setEditable(true);
                                    topologyLink.interfaceList4.getSelectionModel().select(linkValues[5]);
                                }
                            }
                        }
                    }

                    for (String string : draggedImagesName) {
                        topologyLink.devicesInTopoEditor.getItems().add(string);
                        topologyLink.destDevicesInTopoEditor.getItems().add(string);
                    }

                    topologyLink.devicesInTopoEditor.setOnAction(new EventHandler<ActionEvent>() {
                        @Override
                        public void handle(ActionEvent arg0) {
                            topologyLink.interfaceList2.getItems().clear();
                            try {
                                for (HashMap<String, String> interFaceDetail : arrayOfInterFaceHash) {
                                    Set set = interFaceDetail.entrySet();
                                    Iterator interFaceHashDetailIterator = set.iterator();
                                    while (interFaceHashDetailIterator.hasNext()) {
                                        Map.Entry me = (Map.Entry) interFaceHashDetailIterator.next();
                                        String[] deviceNameAndiniterFaceValue = me.getValue().toString().split("\\_");
                                        if (deviceNameAndiniterFaceValue[1].equals(topologyLink.devicesInTopoEditor.getSelectionModel().getSelectedItem())) {
                                            if (!me.getKey().toString().equals("")) {
                                                topologyLink.interfaceList2.getItems().add(me.getKey().toString());
                                            }
                                        }
                                    }
                                }
                            } catch (Exception e) {
                            }
                        }
                    });

                    topologyLink.destDevicesInTopoEditor.setOnAction(new EventHandler<ActionEvent>() {
                        @Override
                        public void handle(ActionEvent arg0) {

                            topologyLink.interfaceList4.getItems().clear();
                            try {
                                for (HashMap<String, String> interFaceDetail : arrayOfInterFaceHash) {
                                    Set set = interFaceDetail.entrySet();
                                    Iterator interFaceHashDetailIterator = set.iterator();
                                    while (interFaceHashDetailIterator.hasNext()) {
                                        Map.Entry me = (Map.Entry) interFaceHashDetailIterator.next();
                                        String[] deviceNameAndiniterFaceValue = me.getValue().toString().split("\\_");

                                        if (deviceNameAndiniterFaceValue[1].equals(topologyLink.destDevicesInTopoEditor.getSelectionModel().getSelectedItem())) {
                                            if (!me.getKey().toString().equals("")) {
                                                topologyLink.interfaceList4.getItems().add(me.getKey().toString());
                                            }
                                        }
                                    }
                                }
                            } catch (Exception e) {
                            }
                        }
                    });

                    topologyLink.finishSelectedLink.setOnAction(new EventHandler<ActionEvent>() {
                        @Override
                        public void handle(ActionEvent arg0) {
                            con11.setId(topologyLink.nameText.getText() + "_" + con11.getStartX() + "_" + con11.getStartY() + "_" + con11.getEndX() + "_" + con11.getEndY());
                            String detailedString = topologyLink.nameText.getText() + "_" + topologyLink.typeText.getText() + "_" + topologyLink.devicesInTopoEditor.getSelectionModel().getSelectedItem() + "_" + topologyLink.interfaceList2.getSelectionModel().getSelectedItem() + "_" + topologyLink.destDevicesInTopoEditor.getSelectionModel().getSelectedItem() + "_" + topologyLink.interfaceList4.getSelectionModel().getSelectedItem() + "_";
                            linkTopologyHash.put(con11.getId(), detailedString);
                            arrayOfLinkTopologyHash = new ArrayList<HashMap<String, String>>();
                            arrayOfLinkTopologyHash.add(linkTopologyHash);
                            topologyLink.copyStage.close();
                        }
                    });


                }
                if (arg0.getButton() == MouseButton.SECONDARY) {
                    deleteLineContextMenu(contentLine, con11, arg0);

                }
            }
        });

    }

    void insertImage1(Image i, Tab hb) {
        ImageView iv = new ImageView();
        iv.setImage(i);
        setupGestureSource(iv);
    }

    void setupGestureTarget(final HBox targetBox) {
        targetBox.setOnDragOver(new EventHandler<DragEvent>() {
            @Override
            public void handle(DragEvent event) {
                Dragboard db = event.getDragboard();
                if (db.hasImage()) {
                    event.acceptTransferModes(TransferMode.COPY);
                }
                event.consume();
            }
        });

        targetBox.setOnDragDropped(new EventHandler<DragEvent>() {
            @Override
            public void handle(DragEvent event) {
               Dragboard db = event.getDragboard();
                if (db.hasImage()) {
                    event.setDropCompleted(true);
                } else {
                    event.setDropCompleted(false);
                }
                event.consume();
            }
        });
    }

    void setupGestureSource(final ImageView source) {
        source.setOnDragDetected(new EventHandler<MouseEvent>() {
            @Override
            public void handle(MouseEvent event) {

                /*
                 * allow any transfer mode
                 */
                Dragboard db = source.startDragAndDrop(TransferMode.COPY);

                /*
                 * put a image on dragboard
                 */
                ClipboardContent content = new ClipboardContent();

                Image sourceImage = source.getImage();
                content.putImage(sourceImage);
                db.setContent(content);

                event.consume();
            }
        });

    }

    void deleteLineContextMenu(final DraggableNode contentLine, final Line connecting, MouseEvent arg0) {

        ContextMenu menu = new ContextMenu();
        MenuItem item = new MenuItem("Delete Line");
        item.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent arg0) {
                contentLine.setVisible(false);
                contentLine.getChildren().remove(connecting);
            }
        });

        menu.getItems().add(item);
        menu.show(contentLine, arg0.getScreenX(), arg0.getScreenY());

    }

    public ArrayList<TextField> getDeviceNameList() {
        return deviceNameList;
    }

    public ArrayList<String> getPropertyDetail() {
        return propertyValue;
    }

    class Anchor extends Circle {

        Anchor(String id, DoubleProperty x, DoubleProperty y) {
            super(x.get(), y.get(), 7);
            setId(id);
            setFill(Color.ANTIQUEWHITE.deriveColor(1, 1, 1, 0.75));
            setStroke(Color.GREY);
            x.bind(centerXProperty());
            y.bind(centerYProperty());
        }
    }

    class Anchor2 extends DraggableNode {

        Anchor2(String id, DoubleProperty x, DoubleProperty y) {
            super();
            setId(id);

            x.bind(layoutXProperty());
            y.bind(layoutYProperty());
        }
    }

    private void enableDragLineWithAnchors(final Line connecting, final Circle anchor1, final Circle anchor2) {
        final Delta dragDelta = new Delta();

        connecting.setOnMousePressed(new EventHandler<MouseEvent>() {
            @Override
            public void handle(MouseEvent mouseEvent) {
                // record a delta distance for the drag and drop operation.
                dragDelta.x = connecting.getLayoutX() - mouseEvent.getX();
                dragDelta.y = connecting.getLayoutY() - mouseEvent.getY();
                dragDelta.x = anchor1.getLayoutX() - mouseEvent.getX();
                dragDelta.y = anchor1.getLayoutY() - mouseEvent.getY();
                dragDelta.x = anchor2.getLayoutX() - mouseEvent.getX();
                dragDelta.y = anchor2.getLayoutY() - mouseEvent.getY();
                connecting.getScene().setCursor(Cursor.MOVE);
            }
        });
        connecting.setOnMouseReleased(new EventHandler<MouseEvent>() {
            @Override
            public void handle(MouseEvent mouseEvent) {
                connecting.getScene().setCursor(Cursor.HAND);
            }
        });
        connecting.setOnMouseDragged(new EventHandler<MouseEvent>() {
            @Override
            public void handle(MouseEvent mouseEvent) {
                connecting.setLayoutX(mouseEvent.getX() + dragDelta.x);
                connecting.setLayoutY(mouseEvent.getY() + dragDelta.y);
                anchor1.setLayoutX(mouseEvent.getX() + dragDelta.x);
                anchor1.setLayoutY(mouseEvent.getY() + dragDelta.y);
                anchor2.setLayoutX(mouseEvent.getX() + dragDelta.x);
                anchor2.setLayoutY(mouseEvent.getY() + dragDelta.y);

            }
        });
        connecting.setOnMouseEntered(new EventHandler<MouseEvent>() {
            @Override
            public void handle(MouseEvent mouseEvent) {
                if (!mouseEvent.isPrimaryButtonDown()) {
                    connecting.getScene().setCursor(Cursor.HAND);
                }
            }
        });

        connecting.setOnMouseExited(new EventHandler<MouseEvent>() {
            @Override
            public void handle(MouseEvent mouseEvent) {
                if (!mouseEvent.isPrimaryButtonDown()) {
                    connecting.getScene().setCursor(Cursor.DEFAULT);
                }
            }
        });
    }

    private void enableDrag(final Circle circle) {
        final TopologyWizard.Delta dragDelta = new TopologyWizard.Delta();
        circle.setOnMousePressed(new EventHandler<MouseEvent>() {
            @Override
            public void handle(MouseEvent mouseEvent) {
                // record a delta distance for the drag and drop operation.
                dragDelta.x = circle.getCenterX() - mouseEvent.getX();
                dragDelta.y = circle.getCenterY() - mouseEvent.getY();
                circle.getScene().setCursor(Cursor.MOVE);
            }
        });
        circle.setOnMouseReleased(new EventHandler<MouseEvent>() {
            @Override
            public void handle(MouseEvent mouseEvent) {
                circle.getScene().setCursor(Cursor.HAND);
            }
        });
        circle.setOnMouseDragged(new EventHandler<MouseEvent>() {
            @Override
            public void handle(MouseEvent mouseEvent) {
                circle.setCenterX(mouseEvent.getX() + dragDelta.x);
                circle.setCenterY(mouseEvent.getY() + dragDelta.y);
            }
        });
        circle.setOnMouseEntered(new EventHandler<MouseEvent>() {
            @Override
            public void handle(MouseEvent mouseEvent) {
                if (!mouseEvent.isPrimaryButtonDown()) {
                    circle.getScene().setCursor(Cursor.HAND);
                }
            }
        });
        circle.setOnMouseExited(new EventHandler<MouseEvent>() {
            @Override
            public void handle(MouseEvent mouseEvent) {
                if (!mouseEvent.isPrimaryButtonDown()) {
                    circle.getScene().setCursor(Cursor.DEFAULT);
                }
            }
        });
    }

    class Delta {

        double x, y;
    }
}
