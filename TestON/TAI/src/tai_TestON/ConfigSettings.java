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

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.Locale;
import java.util.logging.Level;
import java.util.logging.Logger;
import javafx.application.Application;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.geometry.HPos;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Group;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import javafx.scene.paint.Color;
import javafx.scene.shape.Rectangle;
import javafx.stage.Stage;

public class ConfigSettings extends Application {

    GridPane gridpane;
    TAI_TestON referenceOFA;
    TAIFileOperations fileOperations = new TAIFileOperations();
    TAILocale label = new TAILocale(Locale.ENGLISH);
    Stage copyStage;

  
    @Override
    public void start(Stage primaryStage) {
        copyStage = primaryStage;
        final Group group = new Group();
        Scene scene = new Scene(group, 500, 250);


        GridPane gridpane = new GridPane();
        gridpane.setPadding(new Insets(40, 0, 0, 50));
        gridpane.setHgap(5);
        gridpane.setVgap(5);

        Label lbParser = new Label("Parser Location:");
        GridPane.setHalignment(lbParser, HPos.RIGHT);
        final TextField tfParser = new TextField();

        Label lbPass = new Label("Parser Class:");
        GridPane.setHalignment(lbPass, HPos.RIGHT);
        final TextField tfPass = new TextField();

        Label lbLogger = new Label("Logger Location:");
        GridPane.setHalignment(lbPass, HPos.RIGHT);
        final TextField tfField = new TextField();

        Label lbLoggerClass = new Label("Logger Class:");
        GridPane.setHalignment(lbPass, HPos.RIGHT);
        final TextField tfClass = new TextField();
        
        HBox buttonBox = new HBox(10);
        buttonBox.setPadding(new Insets(30, 0, 0, 0));
        
        Button btSave = new Button("save");
        GridPane.setMargin(btSave, new Insets(10, 0, 0, 0));

        Button btRestoreDefaults = new Button("Restore Defaults");
        GridPane.setMargin(btRestoreDefaults, new Insets(10, 0, 0, 20));
 
        buttonBox.getChildren().addAll(btSave,btRestoreDefaults);



        btSave.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent t) {
                String configFileContent = "<config>\n" + "\t<parser>\n" + "\t\t<file>" + tfParser.getText() + "</file>\n" + "\t\t<class>" + tfPass.getText()
                        + "</class>\n" + "\t</parser>\n" + "\t<logger>\n" + "\t\t<file>" + tfField.getText() + "</file>\n" + "\t\t<class>"
                        + tfClass.getText() + "</class>\n" + "\t</logger>\n" + "</config>";
                try {
                    fileOperations.saveFile(new File(label.hierarchyTestON + "config/teston.cfg"), configFileContent);
                    copyStage.close();
                } catch (FileNotFoundException ex) {
                    Logger.getLogger(ConfigSettings.class.getName()).log(Level.SEVERE, null, ex);
                } catch (IOException ex) {
                    Logger.getLogger(ConfigSettings.class.getName()).log(Level.SEVERE, null, ex);
                }

            }
        });


        btRestoreDefaults.setOnAction(new EventHandler<ActionEvent>() {
            @Override
            public void handle(ActionEvent t) {
                tfParser.setText(label.hierarchyTestON + "core/xmlparser.py");
                tfPass.setText("xmlparser");
                tfField.setText(label.hierarchyTestON + "core/logger.py");
                tfClass.setText("Logger");
            }
        });

        gridpane.add(lbParser, 0, 0);
        gridpane.add(tfParser, 1, 0);
        gridpane.add(lbPass, 0, 1);
        gridpane.add(tfPass, 1, 1);
        gridpane.add(lbLogger, 0, 2);
        gridpane.add(tfField, 1, 2);
        gridpane.add(lbLoggerClass, 0, 3);
        gridpane.add(tfClass, 1, 3);
        gridpane.add(buttonBox, 1, 4);
      




        primaryStage.setTitle("Settings");
        primaryStage.setScene(scene);
        primaryStage.setResizable(true);
        primaryStage.sizeToScene();
        primaryStage.show();

        group.getChildren().addAll(gridpane);
        primaryStage.show();
    }
}