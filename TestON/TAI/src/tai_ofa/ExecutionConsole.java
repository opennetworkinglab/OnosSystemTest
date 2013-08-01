/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package tai_ofa;

import javafx.application.Application;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Group;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.Tab;
import javafx.scene.control.TabPane;
import javafx.scene.control.TextField;
import javafx.scene.control.TextFieldBuilder;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.StackPane;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;

/**
 *
 * @author Raghav Kashyap raghavkashyap@paxterrasolutions.com
	
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
public class ExecutionConsole extends Application {
    
    Stage copyStage;
    Scene scene;
    TextField value ;
    String Title,enteredValue ;
    Button submit ;
    ExecutionConsole(String Title,Button enter, TextField value) {
        this.Title = Title;
        this.submit = enter;
        this.value = value;
    }
   
  @Override public void start(final Stage primaryStage) throws Exception {
    copyStage = primaryStage;
    
    Group root = new Group();
    GridPane basePane = new GridPane(); 
    basePane.setPadding(new Insets(2, 0, 2, 0));
    basePane.setVgap(5);
    basePane.setHgap(2);
    value.setEditable(true);
    value.clear();
    enteredValue = "";
    Label info = new Label("Please pass the appropriate value");
    
    
    basePane.add(value, 0, 1);
    basePane.add(submit, 1, 1);
    basePane.add(info, 0, 0);
    scene = new Scene(root, 550, 60);
    
    root.getChildren().addAll(basePane);
    primaryStage.setTitle(Title);  
    primaryStage.setScene(scene);
    primaryStage.show();
  }
  
  public void closeWindow(){
      copyStage.close();
  }
  public void setValue(String value){
      enteredValue = value;
  }
  public String getValue(){
      return enteredValue;
  }

  public void setTitles(String title){
      copyStage.setTitle(title);
  }
  
}
