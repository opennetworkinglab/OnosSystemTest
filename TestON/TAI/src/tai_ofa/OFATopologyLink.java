/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package tai_ofa;

import javafx.application.Application;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.geometry.Insets;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.ComboBox;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
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
class OFATopologyLink extends Application {

    Label device1;
    ComboBox<String> devicesInTopoEditor;
    ComboBox<String> destDevicesInTopoEditor;
    ComboBox<String> interfaceList2;
    ComboBox<String> interfaceList4;
    GridPane propertyGrid = new GridPane();
    Button finishSelectedLink;
    Button cancelButton;
    TextField nameText;
    TextField typeText;
    Stage copyStage;

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        launch(args);
    }

    @Override
    public void start(final Stage primaryStage) {
        copyStage = primaryStage;
        primaryStage.setTitle("Selected Link Popup");
        propertyGrid.setVgap(8);
        propertyGrid.setHgap(30);
        primaryStage.setResizable(false);
        propertyGrid.setPadding(new Insets(10, 0, 0, 50));
        devicesInTopoEditor = new ComboBox<String>();
        interfaceList2 = new ComboBox<String>();
        Label attribute = new Label("Attribute");
        attribute.setStyle("-fx-padding: 0; -fx-background-color: lightgray; -fx-border-width: 2;-fx-border-color: gray;");
        propertyGrid.add(attribute, 0, 1);

        Label value = new Label("Value");
        value.setStyle("-fx-padding: 0; -fx-background-color: lightgray; -fx-border-width: 2;-fx-border-color: gray;");
        propertyGrid.add(value, 1, 1);
        Label name = new Label("Name");
        propertyGrid.add(name, 0, 2);
        nameText = new TextField();
        propertyGrid.add(nameText, 1, 2);

        Label type = new Label("Type");
        propertyGrid.add(type, 0, 3);
        typeText = new TextField();
        propertyGrid.add(typeText, 1, 3);
        device1 = new Label("Source Device");
        propertyGrid.add(device1, 0, 4);
        devicesInTopoEditor.setMinWidth(170);
        propertyGrid.add(devicesInTopoEditor, 1, 4);

        Label interface1 = new Label("Interface");
        propertyGrid.add(interface1, 0, 5);
        interfaceList2 = new ComboBox<String>();
        interfaceList2.setMinWidth(170);
        propertyGrid.add(interfaceList2, 1, 5);

        Label device2 = new Label("Destination Device");
        propertyGrid.add(device2, 0, 6);
        destDevicesInTopoEditor = new ComboBox<String>();
        destDevicesInTopoEditor.setMinWidth(170);
        propertyGrid.add(destDevicesInTopoEditor, 1, 6);

        Label device3 = new Label("Interface");
        propertyGrid.add(device3, 0, 7);
        interfaceList4 = new ComboBox<String>();
        interfaceList4.setMinWidth(170);
        propertyGrid.add(interfaceList4, 1, 7);

        HBox propertyButton = new HBox(5);
        propertyButton.setPadding(new Insets(0, 0, 0, 0));
        finishSelectedLink = new Button("Save");

        cancelButton = new Button("Cancel");
        propertyButton.getChildren().addAll(new Label("       "), finishSelectedLink, cancelButton);
        propertyGrid.add(propertyButton, 1, 8);

        cancelButton.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent arg0) {
                primaryStage.close();
            }
        });
        StackPane root = new StackPane();
        root.getChildren().add(propertyGrid);
        primaryStage.setScene(new Scene(root, 450, 320));
        primaryStage.show();
    }
}
