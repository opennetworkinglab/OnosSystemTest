/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package tai_ofa;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Locale;
import javafx.application.Application;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.event.Event;
import javafx.event.EventHandler;
import javafx.geometry.Insets;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.ComboBox;
import javafx.scene.control.Label;
import javafx.scene.control.PasswordField;
import javafx.scene.control.RadioButton;
import javafx.scene.control.Tab;
import javafx.scene.control.TabPane;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableColumn.CellEditEvent;
import javafx.scene.control.TableView;
import javafx.scene.control.TextField;
import javafx.scene.control.TextFieldBuilder;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.scene.control.cell.TextFieldTableCell;
import javafx.scene.input.KeyCode;
import javafx.scene.input.KeyEvent;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.Pane;
import javafx.stage.Stage;
import sun.misc.Cleaner;

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
public class OFATopology extends Application {

    public OFATopology() {
    }
    ObservableList<OFATopologyInterface> data;
    TableView<OFATopologyInterface> deviceTable;
    TableColumn device;
    TableColumn number;
    TableColumn type;
    int count = 1;
    String getHostName, getUserName, getPassword, getTranportProtocol, getPort;
    ArrayList<String> getAttribute = new ArrayList<String>();
    ArrayList<String> getValue = new ArrayList<String>();
    ArrayList<TextField> attributeList = new ArrayList<TextField>();
    ArrayList<TextField> valueList = new ArrayList<TextField>();
    TextField attributeText;
    Button interFacesave;
    TextField valueText;
    Button save;
    TextField hostNameText;
    TextField userNameText;
    PasswordField passwordText;
    TextField portText;
    TextField deviceText;
    ComboBox<String> transportList;
    Stage copyStage;
    ArrayList<String> propertyDetail = new ArrayList<String>();
    HashMap<TextField, TextField> hashProperty = new HashMap<TextField, TextField>();
    Button defaultButton;
    Button cancelButton;
    RadioButton testTargetRadioButton;
    TAILocale label = new TAILocale(new Locale("en", "EN"));

    /**
     * @param args the command line arguments
     */
    OFATopology(TextField text) {
        deviceText = text;
    }

    @Override
    public void start(final Stage primaryStage) {
        copyStage = primaryStage;
        primaryStage.setTitle(label.topoTitle);
        primaryStage.setResizable(false);
        TabPane toplogyTabPane = new TabPane();
        toplogyTabPane.setMaxHeight(280);
        Tab propertyTab = new Tab(label.topoProperties);
        Tab interfaceTab = new Tab("Component");
        propertyTab.setClosable(false);
        interfaceTab.setClosable(false);
        toplogyTabPane.getTabs().addAll(propertyTab, interfaceTab);

        GridPane propertyGrid = new GridPane();
        propertyGrid.setVgap(8);
        propertyGrid.setHgap(10);
        propertyGrid.setPadding(new Insets(10, 0, 0, 50));

        Label attribute = new Label(label.topoAttribute);
        attribute.setStyle("-fx-padding: 0; -fx-background-color: lightgray; -fx-border-width: 2;-fx-border-color: gray;");
        propertyGrid.add(attribute, 0, 1);

        Label value = new Label(label.topoValue);
        value.setStyle("-fx-padding: 0; -fx-background-color: lightgray; -fx-border-width: 2;-fx-border-color: gray;");
        propertyGrid.add(value, 1, 1);

        Label hostName = new Label(label.topoHost);
        propertyGrid.add(hostName, 0, 2);
        hostNameText = new TextField();
        propertyGrid.add(hostNameText, 1, 2);
        Label userName = new Label(label.topoUserName);
        propertyGrid.add(userName, 0, 3);
        userNameText = new TextField();
        propertyGrid.add(userNameText, 1, 3);
        Label password = new Label(label.topoPassword);
        propertyGrid.add(password, 0, 4);
        passwordText = new PasswordField();
        propertyGrid.add(passwordText, 1, 4);
        Label transport = new Label(label.topoTransport);
        transportList = new ComboBox<String>();
        transportList.setMinWidth(200);
        transportList.getItems().addAll(label.topoSSH, label.topoTELNET, label.topoFTP, label.topoRLOGIN);
        Label testTargetLabel = new Label("Test Target");
        propertyGrid.add(testTargetLabel, 0, 5);
        testTargetRadioButton = new RadioButton("True");
        propertyGrid.add(testTargetRadioButton, 1, 5);
        HBox propertyButton = new HBox(5);

        propertyButton.setPadding(new Insets(280, 0, 0, 140));
        save = new Button(label.topoSave);
        defaultButton = new Button(label.topoDefault);
        cancelButton = new Button(label.topoCancel);
        propertyButton.getChildren().addAll(save, defaultButton, cancelButton);
        propertyTab.setContent(propertyGrid);

        //  interface tab code 
        GridPane interfaceGridPane = new GridPane();
        interfaceGridPane.setVgap(20);
        interfaceGridPane.setHgap(20);
        interfaceGridPane.setPadding(new Insets(10, 0, 0, 10));
        Label interFaceNumber = new Label("" + count);
        attributeText = new TextField();
        valueText = new TextField();

        valueText.setOnKeyPressed(new EventHandler<KeyEvent>() {
            @Override
            public void handle(KeyEvent keyEvent) {
                if (keyEvent.getCode() == KeyCode.ENTER) {
                    deviceTable.getSelectionModel().select(deviceTable.getItems().size() - 1);
                    if (deviceTable.getSelectionModel().isSelected(deviceTable.getItems().size() - 1)) {
                        if (!deviceTable.getSelectionModel().getSelectedItem().getDeviceName().getText().equals("") && !deviceTable.getSelectionModel().getSelectedItem().getDeviceType().getText().equals("")) {
                            addInterFace();
                        }
                    }
                }
            }
        });

        deviceTable = new TableView<OFATopologyInterface>();
        data = FXCollections.observableArrayList(new OFATopologyInterface(interFaceNumber, attributeText, valueText));
        deviceTable.setMinWidth(330);
        deviceTable.setMaxHeight(200);
        number = new TableColumn(label.topoInterfaces);
        number.setCellValueFactory(new PropertyValueFactory<OFATopologyInterface, Label>("interFaceNumber"));
        number.setMinWidth(90);
        number.setResizable(false);
        device = new TableColumn(label.topoAttribute);
        device.setCellValueFactory(new PropertyValueFactory<OFATopologyInterface, TextField>("deviceName"));
        device.setMaxWidth(119);
        device.setResizable(false);
        type = new TableColumn(label.topoValues);
        type.setCellValueFactory(new PropertyValueFactory<OFATopologyInterface, TextField>("deviceType"));
        type.setMaxWidth(119);
        type.setResizable(false);
        deviceTable.setItems(data);
        deviceTable.getColumns().addAll(number, device, type);
        interfaceGridPane.add(deviceTable, 0, 1);
        interfaceTab.setContent(interfaceGridPane);
        HBox interFaceButton = new HBox(5);
        interFaceButton.setPadding(new Insets(0, 0, 0, 2));
        attributeList.add(attributeText);
        valueList.add(valueText);
        hashProperty.put(attributeText, valueText);

        interfaceGridPane.add(interFaceButton, 0, 2);
        Pane root = new Pane();
        root.getChildren().addAll(propertyButton, toplogyTabPane);
        primaryStage.setScene(new Scene(root, 350, 300));
        primaryStage.show();
    }

    public void addInterFace() {
        int intNumber = ++count;
        Label interFaceNumber = new Label("" + intNumber);
        attributeText = new TextField();
        attributeList.add(attributeText);
        valueText = new TextField();
        attributeText.setMaxWidth(120);
        valueText.setMinWidth(120);
        hashProperty.put(attributeText, valueText);
        for (int i = 0; i < deviceTable.getItems().size(); i++) {
            deviceTable.getSelectionModel().select(deviceTable.getItems().size() - 1);
        }

        deviceTable.getSelectionModel().select(deviceTable.getItems().size());
        valueText.setOnKeyPressed(new EventHandler<KeyEvent>() {
            @Override
            public void handle(KeyEvent keyEvent) {
                if (keyEvent.getCode() == KeyCode.ENTER) {
                    deviceTable.getSelectionModel().select(deviceTable.getItems().size() - 1);
                    if (deviceTable.getSelectionModel().isSelected(deviceTable.getItems().size() - 1)) {
                        if (!deviceTable.getSelectionModel().getSelectedItem().getDeviceName().getText().equals("") && !deviceTable.getSelectionModel().getSelectedItem().getDeviceType().getText().equals("")) {
                            addInterFace();
                        }
                    }

                }
            }
        });
        valueList.add(valueText);
        data.add(new OFATopologyInterface(interFaceNumber, attributeText, valueText));
        number.setCellValueFactory(new PropertyValueFactory<OFATopologyInterface, Label>("interFaceNumber"));
        number.setMinWidth(90);
        number.setResizable(false);
        device.setCellValueFactory(new PropertyValueFactory<OFATopologyInterface, TextField>("deviceName"));
        device.setMaxWidth(120);
        device.setResizable(false);
        type.setCellValueFactory(new PropertyValueFactory<OFATopologyInterface, TextField>("deviceType"));
        type.setMaxWidth(120);
        type.setResizable(false);
        deviceTable.setItems(data);
        deviceTable.setEditable(true);
    }

    public String getHostName() {
        return getHostName;
    }

    public String getUserName() {
        return getUserName;
    }

    public String getPassword() {
        return getPassword;
    }

    public String getTransportProtocool() {
        return getTranportProtocol;
    }

    public String getPort() {
        return getPort;
    }

    public ArrayList getAtttribute() {
        return getAttribute;
    }

    public ArrayList getValue() {
        return getValue;
    }
}
