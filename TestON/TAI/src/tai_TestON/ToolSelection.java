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
import java.net.MalformedURLException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;
import java.util.Vector;
import java.util.logging.Level;
import java.util.logging.Logger;
import javafx.application.Application;
import javafx.beans.value.ChangeListener;
import javafx.beans.value.ObservableValue;
import javafx.collections.ObservableList;
import javafx.event.ActionEvent;
import javafx.event.Event;
import javafx.event.EventHandler;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Group;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.RadioButton;
import javafx.scene.control.Tab;
import javafx.scene.control.Toggle;
import javafx.scene.control.ToggleGroup;
import javafx.scene.control.Tooltip;
import javafx.scene.input.InputEvent;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import javafx.scene.layout.VBoxBuilder;
import javafx.scene.text.Text;
import javafx.stage.Modality;
import javafx.stage.Stage;
import javax.swing.JOptionPane;
import org.apache.xmlrpc.XmlRpcClient;
import org.apache.xmlrpc.XmlRpcException;

/**
 *
 * @author paxterra
 */
public class ToolSelection extends Application{

    Scene scene;
    Stage primaryStage;
    GridPane baseGridPane;
    int selectionId = 0;
    
    @Override
    public void start(Stage stage) throws Exception {
        primaryStage = stage;
        Group rootGroup = new Group();
        baseGridPane = new GridPane();
        
        getContent();
        
        
        rootGroup.getChildren().addAll(baseGridPane);
        scene = new Scene(rootGroup, 350, 250);
        
        stage.setTitle("-- Tool Selection --");
        stage.setScene(scene);
        stage.setResizable(true);
        stage.sizeToScene();
        stage.show();
    }
    
    public void getContent(){
        
        final RadioButton updateDriver = new RadioButton("Update Driver at API level");
        updateDriver.setTooltip(new Tooltip("updating the existin drivers at API level"));
        
        
        final RadioButton generateDriver = new RadioButton("Generate Driver for CLI");
        generateDriver.setTooltip(new Tooltip("Generate Driver to generate drivers adding methods to driver for CLI"));
        
        ToggleGroup group = new ToggleGroup();
        group.getToggles().addAll(updateDriver,generateDriver); 
        
        baseGridPane.setPadding(new Insets(30, 0, 0, 40));
        baseGridPane.setHgap(0);
        baseGridPane.setVgap(5);
        final Button okayButton = new Button("OK");
        okayButton.setDisable(true);
        
        group.selectedToggleProperty().addListener(new ChangeListener<Toggle>() {

            @Override
            public void changed(ObservableValue<? extends Toggle> ov, Toggle t, Toggle t1) {
                okayButton.setDisable(false);
            }
        });
        
        
        okayButton.setOnAction(new EventHandler<ActionEvent>() {

            @Override
            public void handle(ActionEvent t) {
               if(updateDriver.selectedProperty().get()){
                   selectionId++;
                   DriverTools toolsWindow = new DriverTools(selectionId);
                    try {
                        primaryStage.close();
                        toolsWindow.start(new Stage());
                    } catch (Exception ex) {
                        Logger.getLogger(ToolSelection.class.getName()).log(Level.SEVERE, null, ex);
                    }
                    
               } else if(generateDriver.selectedProperty().get()){
                   selectionId = selectionId + 2;
                   DriverTools toolsWindow = new DriverTools(selectionId);
                    try {
                        primaryStage.close();
                        toolsWindow.start(new Stage());
                    } catch (Exception ex) {
                        Logger.getLogger(ToolSelection.class.getName()).log(Level.SEVERE, null, ex);
                    }
               }
            }
        });
        
        
        baseGridPane.add(updateDriver, 2, 2);
        baseGridPane.add(generateDriver, 2, 5);
        
        HBox buttonBox = new HBox();
        buttonBox.setSpacing(20);
        buttonBox.setPadding(new Insets(100, 50, 10, 50));
        
        
        
        Button cancelButton = new Button("Cancel");
        
        buttonBox.getChildren().addAll(okayButton,cancelButton);
        
        baseGridPane.add(buttonBox, 2, 6);
        
        
        
        
    }
    
    
   
     
    
}
