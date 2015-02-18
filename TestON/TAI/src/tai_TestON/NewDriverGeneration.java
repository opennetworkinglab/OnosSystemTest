/*
 * @author : Raghav Kashyap (raghavkashyap@paxterrasolutions.com)
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

import com.sun.javafx.scene.control.FocusableTextField;
import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Locale;
import java.util.logging.Level;
import java.util.logging.Logger;
import javafx.application.Application;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.geometry.Insets;
import javafx.scene.Group;
import javafx.scene.Node;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.TextField;
import javafx.scene.control.TreeItem;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.input.KeyEvent;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import javafx.scene.paint.Color;
import javafx.scene.text.Text;
import javafx.stage.DirectoryChooser;
import javafx.stage.Stage;

/**
 *
 * @author paxterra
 */
public class NewDriverGeneration extends Application {

    Scene scene;
    GridPane selectionAreaPane;
    DriverTools toolsReference;
    TAILocale label = new TAILocale(Locale.ENGLISH);
    File selectedDirectory;
    Button save;
    TextField driverName,driverPath;
    Stage copyStage;
    public NewDriverGeneration(DriverTools driversTool){
        this.toolsReference = driversTool;
    }
    
    
    @Override
    public void start(Stage primaryStage) throws Exception {
        copyStage = primaryStage;
        VBox baseBox = new VBox(10);
        selectionAreaPane = new GridPane();
        selectionAreaPane.setPadding(new Insets(5, 0, 10, 10));
        selectionAreaPane.setHgap(10);
        selectionAreaPane.setVgap(10);
        
        HBox buttonBox = new HBox(10);
        buttonBox.setPadding(new Insets(0, 0, 5, 40));
        save = new Button("Finish");
        Button cancel = new Button("Cancel");
        buttonBox.getChildren().addAll(save,cancel);
        getSelectionInterface();
        
        save.setDisable(true);
        
        save.setOnAction(new EventHandler<ActionEvent>() {

            @Override
            public void handle(ActionEvent t) {
                String driverPathWithName = driverPath.getText() + "/" + driverName.getText() + ".py";
                try {
                    new File(driverPathWithName).createNewFile();
                    String projectWorkSpacePath = label.hierarchyTestON + "/drivers/common";
  
                    Path name = new File(projectWorkSpacePath).toPath();
                    TAILoadTree treeNode = new TAILoadTree(name);
                    treeNode.setExpanded(true);
                    toolsReference.driverExplorerTree = treeNode;
                    toolsReference.driverExplorerTreeView.setRoot(treeNode);
                    copyStage.close();
                    
                } catch (IOException ex) {
                    Logger.getLogger(NewDriverGeneration.class.getName()).log(Level.SEVERE, null, ex);
                }
            }
        });
        
        
       baseBox.getChildren().addAll(selectionAreaPane,buttonBox);
       
       Group baseGroup = new Group();
       baseGroup.getChildren().add(baseBox);
       scene = new Scene(baseGroup, 580, 150);
       
       primaryStage.setScene(scene);
       primaryStage.setTitle("New Driver ");
       primaryStage.setResizable(false);
       primaryStage.show();
    }
    
    public void getSelectionInterface(){
        
        Label fileName = new Label("Driver Name :");
        Label driverLocation = new Label("Driver Location");
        
        driverName = new TextField();
        driverPath =  new TextField();
        
        driverName.setMinWidth(320);
        driverPath.setMinWidth(380);
        final Text error = new Text();
        
        selectionAreaPane.add(error, 1, 2);
        
        driverName.setOnKeyReleased(new EventHandler<KeyEvent>() {

            @Override
            public void handle(KeyEvent t) {
                if(driverName.getText().isEmpty()){
                    error.setText("Please Specify Driver Name");
                    error.setFill(Color.RED);
                }else {
                    error.setText("");
                    driverPath.setOnKeyReleased(new EventHandler<KeyEvent>() {

                        @Override
                        public void handle(KeyEvent t) {
                            
                            
                            if (driverPath.getText().isEmpty()){
                                error.setText("Please select the driver folder");
                                error.setFill(Color.RED);
                                save.setDisable(true);
                                
                            }else {
                               error.setText("");
                               save.setDisable(false);
                            }
                            
                        }
                    });
                }
            }
        });
        
        selectionAreaPane.add(fileName, 0, 0);
        selectionAreaPane.add(driverName, 1, 0);
        selectionAreaPane.add(driverLocation, 0, 1);
        selectionAreaPane.add(driverPath, 1, 1);
        
        Button selectPath = new Button("Select");
        HBox folderSelectionBox = new HBox(5);
        
        folderSelectionBox.getChildren().addAll(selectPath);
        
        selectionAreaPane.add(folderSelectionBox, 2, 1);
        
        
        
        selectPath.setOnAction(new EventHandler<ActionEvent>() {

            @Override
            public void handle(ActionEvent t) {
               String selectedPath = chooseDirectory();
               driverPath.setText(selectedPath);
               save.setDisable(false);
            }
        });
        
    }
    
    
    public String chooseDirectory(){
         DirectoryChooser chooser = new DirectoryChooser();
         chooser.setTitle("Select Driver");
         File defaultDirectory = new File(label.hierarchyTestON + "drivers/common/");
         chooser.setInitialDirectory(defaultDirectory);
         selectedDirectory = chooser.showDialog(new Stage() );
        
         return selectedDirectory.toString();
    }
  
}
