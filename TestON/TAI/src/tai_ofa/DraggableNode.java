package tai_ofa;


import javafx.collections.ObservableList;
import javafx.event.EventHandler;
import javafx.scene.Parent;
import javafx.scene.input.MouseEvent;

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
public class DraggableNode extends Parent{

    //ATTRIBUTES
    //X AND Y postion of Node
    double x = 0;
    double y = 0;
    //X AND Y position of mouse
    double mousex=0;
    double mousey=0;

    //To make this function accessible for other Class
    @Override
    public ObservableList getChildren(){
        return super.getChildren();
    }

    public DraggableNode(){
        super();

        //EventListener for MousePressed
        onMousePressedProperty().set(new EventHandler<MouseEvent>(){

            @Override
            public void handle(MouseEvent event) {
               //record the current mouse X and Y position on Node
               mousex = event.getSceneX();
               mousey= event.getSceneY();
               //get the x and y position measure from Left-Top
               x = getLayoutX();
               y = getLayoutY();
            }

        });

        //Event Listener for MouseDragged
        onMouseDraggedProperty().set(new EventHandler<MouseEvent>(){

            @Override
            public void handle(MouseEvent event) {
                //Get the exact moved X and Y
                x += event.getSceneX()-mousex ;
                y += event.getSceneY()-mousey ;

                //set the positon of Node after calculation
                setLayoutX(x);
                setLayoutY(y);

                //again set current Mouse x AND y position
                mousex = event.getSceneX();
                mousey= event.getSceneY();

            }
        });
    }
}
