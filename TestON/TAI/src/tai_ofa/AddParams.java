/*

 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package tai_ofa;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Observable;
import java.util.logging.Level;
import java.util.logging.Logger;
import javafx.beans.property.SimpleStringProperty;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.event.ActionEvent;
import javafx.event.Event;
import javafx.event.EventHandler;
import javafx.geometry.Insets;
import javafx.geometry.Orientation;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.SplitPane;
import javafx.scene.control.Tab;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableColumn.CellEditEvent;
import javafx.scene.control.TableView;
import javafx.scene.control.TextField;
import javafx.scene.control.TextFieldBuilder;
import javafx.scene.control.TreeItem;
import javafx.scene.control.TreeView;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.scene.control.cell.TextFieldTableCell;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.input.KeyEvent;
import javafx.scene.input.MouseEvent;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.Pane;
import javafx.scene.layout.VBox;
import javafx.scene.paint.Color;
import javafx.scene.text.Font;
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
public class AddParams {

    TAI_OFA referenceOFA;
    boolean splitFlag = false;
    Map<String, Object> paramsHash;
    TreeView<String> paramsTreeView;
    TextField Value, tableAttrib, tableValue;
    TableView<ParamsAttribute> attributeTable;
    ObservableList<ParamsAttribute> data;
    Button save, Cancel, edit, add, saveParams;
    HBox buttonBox, tableViewBox, baseLeftPane;
    VBox box, buttonTableVBox;
    GridPane buttonBoxPane, baseRightPane;
    TreeItem<String> params;
    Pane tableViewPane;
    Text Heading;
    String tabValue, tabs;
    OFAWizard wizard;
    OFAFileOperations fileOperations;
    Tab baseTab;
    Button delete;

    public void setOFA(TAI_OFA ofa) {
        this.referenceOFA = ofa;
    }

    public void getNewParams() {
        baseTab = new Tab();
        paramsHash = new HashMap<String, Object>();
        fileOperations = new OFAFileOperations();
        final SplitPane basePane = new SplitPane();
        basePane.setOrientation(Orientation.HORIZONTAL);
        baseLeftPane = new HBox(30);
        params = new TreeItem<String>();
        params.setValue("params");
        TreeItem<String> log_dir = new TreeItem<String>();
        log_dir.setValue("log_dir");
        ImageView logIView = new ImageView(new Image("images/parameter.jpg", 20, 20, true, true));
        logIView.setId("/home/paxterra/");
        log_dir.setGraphic(logIView);
        TreeItem<String> mail = new TreeItem<String>();
        mail.setValue("mail");
        ImageView mailIView = new ImageView(new Image("images/parameter.jpg", 20, 20, true, true));
        mailIView.setId("raghavkashyap@paxterrasolution.com");
        mail.setGraphic(mailIView);
        TreeItem<String> testcases = new TreeItem<String>();
        testcases.setValue("testcases");
        ImageView testIView = new ImageView(new Image("images/parameter.jpg", 20, 20, true, true));
        testIView.setId("1");
        testcases.setGraphic(testIView);
        data = FXCollections.observableArrayList();
        params.getChildren().addAll(testcases, mail, log_dir);
        paramsTreeView = new TreeView<String>(params);
        saveParams = new Button("Save");
        delete = new Button("Delete");
        baseLeftPane.getChildren().addAll(paramsTreeView, saveParams, delete);
        baseRightPane = new GridPane();
        Value = TextFieldBuilder.create().build();
        delete.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent t) {
                removeParamsValue(paramsTreeView.getSelectionModel().getSelectedItem());
            }
        });

        saveParams.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent t) {
                tabs = getParams(params);
                referenceOFA.paramsFileContent = tabs;
                wizard = new OFAWizard(referenceOFA.projectExplorerTree, 2, referenceOFA.projectExplorerTree.getChildren(), referenceOFA.projectExplorerTreeView);
                wizard.setOFA(referenceOFA);
                try {
                    wizard.start(new Stage());
                } catch (Exception ex) {
                    Logger.getLogger(AddParams.class.getName()).log(Level.SEVERE, null, ex);
                }

            }
        });
        save = new Button("Save");
        Cancel = new Button("Cancel");
        edit = new Button("Edit");
        attributeTable = new TableView<ParamsAttribute>();
        attributeTable.setEditable(true);
        TableColumn attribColumn = new TableColumn("Attribute");
        attribColumn.setCellValueFactory(new PropertyValueFactory<ParamsAttribute, String>("Attribute"));
        TableColumn valueColumn = new TableColumn("Value");
        valueColumn.setCellValueFactory(new PropertyValueFactory<ParamsAttribute, String>("Values"));
        attributeTable.setItems(data);
        attributeTable.getColumns().addAll(attribColumn, valueColumn);
        baseRightPane.setPadding(new Insets(30, 0, 10, 30));
        baseRightPane.prefHeight(referenceOFA.scene.heightProperty().get());
        baseRightPane.setVgap(9);
        baseRightPane.add(new Label("Value :"), 4, 4);
        baseRightPane.add(Value, 5, 4);
        box = new VBox();
        buttonBox = new HBox();
        buttonBoxPane = new GridPane();
        buttonBoxPane.setPadding(new Insets(30, 0, 10, 30));
        buttonBoxPane.setHgap(3);
        buttonBoxPane.add(save, 2, 7);
        buttonBoxPane.add(Cancel, 4, 7);
        buttonBoxPane.add(edit, 6, 7);
        buttonBox.getChildren().addAll(buttonBoxPane);
        tableAttrib = TextFieldBuilder.create().build();
        tableValue = TextFieldBuilder.create().build();
        add = new Button("Add");
        tableViewPane = new Pane();
        buttonTableVBox = new VBox();
        tableViewBox = new HBox();
        tableViewBox.getChildren().addAll(tableAttrib, tableValue, add);
        buttonTableVBox.getChildren().addAll(attributeTable);
        box.getChildren().addAll(baseRightPane, buttonTableVBox, buttonBoxPane);

        attributeTable.setEditable(true);
        attribColumn.setCellFactory(TextFieldTableCell.forTableColumn());
        attribColumn.setOnEditCommit(new EventHandler<CellEditEvent<ParamsAttribute, String>>() {
            @Override
            public void handle(CellEditEvent<ParamsAttribute, String> t) {

                for (int i = 0; i < paramsTreeView.getSelectionModel().getSelectedItem().getChildren().size(); i++) {

                    if (paramsTreeView.getSelectionModel().getSelectedItem().getChildren().get(i).getValue().equals(t.getOldValue())) {
                        paramsTreeView.getSelectionModel().getSelectedItem().getChildren().get(i).setValue(t.getNewValue());
                    }
                }
                ((ParamsAttribute) t.getTableView().getItems().get(
                        t.getTablePosition().getRow())).setAttribute(t.getNewValue());

            }
        });

        valueColumn.setCellFactory(TextFieldTableCell.forTableColumn());
        valueColumn.setOnEditCommit(new EventHandler<CellEditEvent<ParamsAttribute, String>>() {
            @Override
            public void handle(CellEditEvent<ParamsAttribute, String> t) {
                for (int i = 0; i < paramsTreeView.getSelectionModel().getSelectedItem().getChildren().size(); i++) {
                    if (paramsTreeView.getSelectionModel().getSelectedItem().getChildren().get(i).getValue().equals(t.getOldValue())) {
                        paramsTreeView.getSelectionModel().getSelectedItem().getChildren().get(i).getGraphic().setId(t.getNewValue());
                    }
                }
                ((ParamsAttribute) t.getTableView().getItems().get(
                        t.getTablePosition().getRow())).setValues(t.getNewValue());
            }
        });

        Value.setOnKeyReleased(new EventHandler<KeyEvent>() {
            @Override
            public void handle(KeyEvent t) {
                if (Value.getText().isEmpty()) {
                    edit.setDisable(false);
                } else {
                    edit.setDisable(true);
                }
            }
        });

        Cancel.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent t) {
                basePane.getItems().removeAll(box);
                splitFlag = false;
                baseRightPane.getChildren().remove(Heading);
                edit.setDisable(false);
            }
        });

        save.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent t) {
                String selected = paramsTreeView.getSelectionModel().getSelectedItem().getValue();
                TreeItem<String> selectedTreeItem = paramsTreeView.getSelectionModel().getSelectedItem();
                String attribVal = Value.getText();
                basePane.getItems().removeAll(box);
                splitFlag = false;
                Map<String, Object> prevParent = new HashMap<String, Object>();
                ArrayList<String> names = new ArrayList<String>();
                if (!edit.isDisabled()) {
                    for (int i = 0; i < attributeTable.getItems().size(); i++) {
                        ParamsAttribute table = attributeTable.getItems().get(i);
                        if (selectedTreeItem.getChildren().size() == 0) {
                            TreeItem<String> childNode = new TreeItem<String>();
                            childNode.setValue(table.getAttribute());
                            selectedTreeItem.getChildren().add(childNode);
                            selectedTreeItem.setExpanded(true);
                            Image chidlImage = new Image("images/parameter.jpg", 20, 20, true, true);
                            ImageView childImageView = new ImageView();
                            childImageView.setImage(chidlImage);
                            childImageView.setId(table.getValues());
                            childNode.setGraphic(childImageView);
                        } else if (selectedTreeItem.getChildren().size() > 0) {
                            names.clear();
                            for (int index = 0; index < selectedTreeItem.getChildren().size(); index++) {
                                names.add(selectedTreeItem.getChildren().get(index).getValue());
                            }
                            if (!names.contains(table.getAttribute())) {
                                TreeItem<String> childNode = new TreeItem<String>();
                                childNode.setValue(table.getAttribute());
                                selectedTreeItem.getChildren().addAll(childNode);
                                selectedTreeItem.setExpanded(true);
                                Image chidlImage = new Image("images/parameter.jpg", 20, 20, true, true);
                                ImageView childImageView = new ImageView();
                                childImageView.setImage(chidlImage);
                                childImageView.setId(table.getValues());
                                childNode.setGraphic(childImageView);
                            }
                        }
                    }
                } else {
                    TreeItem<String> selectTreeItem = paramsTreeView.getSelectionModel().getSelectedItem();
                    if (!Value.getText().isEmpty()) {
                        paramsTreeView.getSelectionModel().getSelectedItem().getGraphic().setId(Value.getText());
                    }
                }
                baseRightPane.getChildren().remove(Heading);
                buttonTableVBox.getChildren().removeAll(tableViewBox);
                Value.clear();
            }
        });

        add.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent t) {

                if (tableAttrib.getText().isEmpty() && tableValue.getText().isEmpty()) {
                } else {
                    data.add(new ParamsAttribute(tableAttrib.getText(), tableValue.getText()));
                    tableAttrib.clear();
                    tableValue.clear();
                }
            }
        });


        edit.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent t) {

                buttonTableVBox.getChildren().addAll(tableViewBox);

                Value.setEditable(false);

            }
        });

        basePane.getItems().addAll(baseLeftPane);
        paramsTreeView.setOnMouseClicked(new EventHandler<MouseEvent>() {
            @Override
            public void handle(MouseEvent args0) {
                String selected = paramsTreeView.getSelectionModel().getSelectedItem().getValue();
                TreeItem<String> selectItem = paramsTreeView.getSelectionModel().getSelectedItem();
                if (args0.getClickCount() == 2 & !splitFlag) {
                    Value.setEditable(true);
                    Heading = new Text(selected);
                    Heading.setFont(Font.font("Arial", 20));
                    Heading.setFill(Color.BLUE);
                    baseRightPane.add(Heading, 6, 1);

                    if (selectItem.isLeaf()) {
                        Value.setDisable(false);
                        if (!selectItem.getGraphic().getId().equals("")) {
                            basePane.getItems().addAll(box);
                            splitFlag = true;
                            Value.setText(selectItem.getGraphic().getId());
                            edit.setDisable(true);
                            data.clear();
                        } else {
                            basePane.getItems().addAll(box);
                            splitFlag = true;
                            Value.clear();
                            edit.setDisable(false);
                            data.clear();
                        }
                    } else if (!selectItem.isLeaf()) {
                        Value.clear();
                        Value.setDisable(true);
                        basePane.getItems().addAll(box);
                        splitFlag = true;
                        data.clear();
                        for (int i = 0; i < selectItem.getChildren().size(); i++) {

                            data.add(new ParamsAttribute(selectItem.getChildren().get(i).getValue(), selectItem.getChildren().get(i).getGraphic().getId()));
                        }
                    }

                }
            }
        });
        basePane.prefWidthProperty().bind(referenceOFA.scene.widthProperty().subtract(300));
        basePane.prefHeightProperty().bind(referenceOFA.scene.heightProperty().subtract(120));
        baseTab.setContent(basePane);
        baseTab.setText("Unnamed.params");
        referenceOFA.editorTabPane.getTabs().addAll(baseTab);
    }

    public String getParams(TreeItem<String> treeNode) {
        tabValue = "";
        tabValue = tabValue + "<" + treeNode.getValue() + ">\n";
        if (!treeNode.isLeaf()) {
            for (int i = 0; i < treeNode.getChildren().size(); i++) {
                if (treeNode.getChildren().get(i).isLeaf()) {
                    tabValue = tabValue + "\n<" + treeNode.getChildren().get(i).getValue() + ">" + treeNode.getChildren().get(i).getGraphic().getId()
                            + "</" + treeNode.getChildren().get(i).getValue() + ">\n";
                } else if (!treeNode.getChildren().get(i).isLeaf()) {
                    int index = 0;
                    tabValue = tabValue + "\n<" + treeNode.getChildren().get(i).getValue() + ">\n";
                    while (index < treeNode.getChildren().get(i).getChildren().size()) {
                        tabValue = tabValue + getParams(treeNode.getChildren().get(i).getChildren().get(index));
                        index++;
                    }
                    tabValue = tabValue + "\n</" + treeNode.getChildren().get(i).getValue() + ">\n";
                }
            }
        } else if (treeNode.isLeaf()) {
            tabValue = tabValue + treeNode.getGraphic().getId();
        }
        tabValue = tabValue + "\n</" + treeNode.getValue() + ">";
        return tabValue;
    }

    public void removeParamsValue(TreeItem treeItem) {
        for (int i = 0; i < paramsTreeView.getRoot().getChildren().size(); i++) {
            if (paramsTreeView.getRoot().getChildren().get(i).isLeaf()) {
                if (paramsTreeView.getRoot().getChildren().get(i).getValue().equals(treeItem.getValue())) {
                    paramsTreeView.getRoot().getChildren().remove(paramsTreeView.getRoot().getChildren().get(i));
                }
            } else if (!paramsTreeView.getRoot().getChildren().get(i).isLeaf()) {
                if (paramsTreeView.getRoot().getChildren().get(i).getValue().equals(treeItem.getValue())) {
                    paramsTreeView.getRoot().getChildren().remove(paramsTreeView.getRoot().getChildren().get(i));
                } else {
                    for (int index = 0; index < paramsTreeView.getRoot().getChildren().get(i).getChildren().size(); index++) {
                        if (paramsTreeView.getRoot().getChildren().get(i).getChildren().get(index).getValue().equals(treeItem.getValue())) {
                            paramsTreeView.getRoot().getChildren().get(i).getChildren().remove(paramsTreeView.getRoot().getChildren().get(i).getChildren().get(index));
                        }
                    }
                }
            }
        }

    }

    public static class ParamsAttribute {
        private final SimpleStringProperty Attributes;
        private final SimpleStringProperty Values;

        private ParamsAttribute(String attrib, String val) {
            this.Attributes = new SimpleStringProperty(attrib);
            this.Values = new SimpleStringProperty(val);
        }

        public String getAttribute() {
            return Attributes.get();
        }

        public void setAttribute(String attrib) {
            Attributes.set(attrib);
        }

        public String getValues() {
            return Values.get();
        }

        public void setValues(String val) {
            Values.set(val);
        }
    }
}
