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
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.attribute.BasicFileAttributes;
import javafx.event.Event;
import javafx.event.EventHandler;
import javafx.scene.Node;
import javafx.scene.control.TreeItem;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;

/**
 *
 * @author Raghav Kashyap (raghavkashyap@paxterrasolutions.com)
 */
public class LoadConfigDirectory extends TreeItem<String> {

    TAIFileOperations fileOperation = new TAIFileOperations();
    public static Image folderCollapseImage = new Image("images/folder.jpg", 30.0, 30.0, true, true);
    public static Image folderExpandImage = new Image("images/folder.jpg", 10.0, 10.0, true, true);
    public static Image fileImage = new Image("images/File.png", 30.0, 30.0, true, true);
    //this stores the full path to the file or directory
    private String fullPath;

    public String getFullPath() {
        return (this.fullPath);
    }
    private boolean isDirectory;

    public boolean isDirectory() {
        return (this.isDirectory);
    }

    public LoadConfigDirectory(Path file) {
        super(file.toString());
        this.fullPath = file.toString();
        //test if this is a directory and set the icon
        if (Files.isDirectory(file)) {
            this.isDirectory = true;
            
                Node rootIcon = new ImageView(new Image(getClass().getResourceAsStream("/images/project.jpeg"), 20, 20, true, true));
                rootIcon.setId("/images/project.jpeg");
                this.setGraphic(rootIcon);
            
        } else {
            this.isDirectory = false;
            String fileName = file.getFileName().toString();
            String ext = fileOperation.getExtension(fileName);
            if (".cfg".equals(ext)) {
                Node rootIcon5 = new ImageView(fileImage);
                rootIcon5.setId(".cfg");
                this.setGraphic(rootIcon5);

            } else if (".log".equals(ext)) {
                Node rootIcon3 = new ImageView(new Image(getClass().getResourceAsStream("/images/log.jpg"), 20, 20, true, true));
                rootIcon3.setId(".log");
                setGraphic(rootIcon3);
            }

            //if you want different icons for different file types this is where you'd do it
        }

        //set the value
        if (!fullPath.endsWith(File.separator)) {
            //set the value (which is what is displayed in the tree)
            String value = file.toString();
            int indexOf = value.lastIndexOf(File.separator);
            if (indexOf > 0) {
                this.setValue(value.substring(indexOf + 1));
            } else {
                this.setValue(value);
            }
        }


        this.addEventHandler(TreeItem.branchExpandedEvent(), new EventHandler() {
            @Override
            public void handle(Event e) {
                LoadConfigDirectory source = (LoadConfigDirectory) e.getSource();
                if (source.isDirectory() && source.isExpanded()) {
                }
                try {
                    if (source.getChildren().isEmpty()) {
                        Path path = Paths.get(source.getFullPath());
                        BasicFileAttributes attribs = Files.readAttributes(path, BasicFileAttributes.class);
                        if (attribs.isDirectory()) {
                            DirectoryStream<Path> dir = Files.newDirectoryStream(path);
                            for (Path file : dir) {
                                LoadConfigDirectory treeNode = new LoadConfigDirectory(file);
                                String fileExtension = fileOperation.getExtension(treeNode.getValue());
                                String fileName = fileOperation.getFileName(treeNode.getValue());
                                if (fileExtension == null || fileExtension.equals(".cfg") || fileExtension.equals(".log")) {
                                    if (fileExtension == null) {
                                        treeNode.setExpanded(true);
                                        source.getChildren().add(treeNode);
                                    } else {
                                        if (fileExtension.matches(".(cfg|log)")) {
                                            String finalValue = treeNode.getValue().replace(fileExtension, "");
                                            treeNode.setValue(finalValue);
                                            if (!treeNode.getValue().equals("__init__")) {
                                                source.getChildren().add(treeNode);
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }

                } catch (Exception ex) {
                }
            }
        });
    }
}
