/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package tai_ofa;

import java.io.File;
import java.io.IOException;
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
public class OFALoadTree extends TreeItem<String> {

    OFAFileOperations fileOperation = new OFAFileOperations();
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

    public OFALoadTree(Path file) {
        super(file.toString());
        this.fullPath = file.toString();
        //test if this is a directory and set the icon
        if (Files.isDirectory(file)) {
            this.isDirectory = true;
            if ("common".equals(file.getFileName().toString())) {
                Node rootIcon = new ImageView(new Image(getClass().getResourceAsStream("/images/project.jpeg"), 20, 20, true, true));
                this.setGraphic(rootIcon);
            } else if ("cli".equals(file.getFileName().toString())) {
                Node rootIcon2 = new ImageView(new Image(getClass().getResourceAsStream("/images/terminal.png"), 20, 20, true, true));
                rootIcon2.setId("/images/terminal.png");
                this.setGraphic(rootIcon2);
            } else if ("api".equals(file.getFileName().toString())) {
                Node rootIcon3 = new ImageView(new Image(getClass().getResourceAsStream("/images/www2.jpg"), 20, 20, true, true));
                this.setGraphic(rootIcon3);
            } else if ("emulator".equals(file.getFileName().toString())) {
                Node rootIcon4 = new ImageView(new Image(getClass().getResourceAsStream("/images/mobile.png"), 20, 20, true, true));
                this.setGraphic(rootIcon4);
            } else if ("tool".equals(file.getFileName().toString())) {
                Node rootIcon5 = new ImageView(new Image(getClass().getResourceAsStream("/images/automatorui.png"), 20, 20, true, true));
                this.setGraphic(rootIcon5);
            } else if ("contoller".equals(file.getFileName().toString())) {
                Node rootIcon6 = new ImageView(new Image(getClass().getResourceAsStream("/images/windows.jpg"), 20, 20, true, true));
                this.setGraphic(rootIcon6);
            } else {
                Node rootIcon = new ImageView(new Image(getClass().getResourceAsStream("/images/project.jpeg"), 20, 20, true, true));
                rootIcon.setId("/images/project.jpeg");
                this.setGraphic(rootIcon);
            }
        } else {
            this.isDirectory = false;
            String fileName = file.getFileName().toString();
            String ext = fileOperation.getExtension(fileName);
            if (".ospk".equals(ext)) {
                Node rootIcon5 = new ImageView(fileImage);
                rootIcon5.setId(".ospk");
                this.setGraphic(rootIcon5);

            } else if (".params".equals(ext)) {
                Node rootIcon1 = new ImageView(new Image(getClass().getResourceAsStream("/images/params.jpeg"), 30, 30, true, true));
                rootIcon1.setId(".params");
                setGraphic(rootIcon1);

            } else if (".topo".equals(ext)) {
                Node rootIcon3 = new ImageView(new Image(getClass().getResourceAsStream("/images/tpl.png"), 30, 30, true, true));
                rootIcon3.setId(".topo");
                setGraphic(rootIcon3);
            } else if (".log".equals(ext)) {
                Node rootIcon3 = new ImageView(new Image(getClass().getResourceAsStream("/images/log.jpg"), 20, 20, true, true));
                rootIcon3.setId(".log");
                setGraphic(rootIcon3);
            } else if (".rpt".equals(ext)) {
                Node rootIcon3 = new ImageView(new Image(getClass().getResourceAsStream("/images/report.jpeg"), 20, 20, true, true));
                rootIcon3.setId(".rpt");
                setGraphic(rootIcon3);
            } else if (".session".equals(ext)) {
                Node rootIcon3 = new ImageView(new Image(getClass().getResourceAsStream("/images/session.png"), 20, 20, true, true));
                rootIcon3.setId(".session");
                setGraphic(rootIcon3);
            } else if (".py".equals(ext)) {
                Node rootIcon3 = new ImageView(new Image(getClass().getResourceAsStream("/images/py.jpg"), 20, 20, true, true));
                rootIcon3.setId(".py");
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
                OFALoadTree source = (OFALoadTree) e.getSource();
                if (source.isDirectory() && source.isExpanded()) {
                }
                try {
                    if (source.getChildren().isEmpty()) {
                        Path path = Paths.get(source.getFullPath());
                        BasicFileAttributes attribs = Files.readAttributes(path, BasicFileAttributes.class);
                        if (attribs.isDirectory()) {
                            DirectoryStream<Path> dir = Files.newDirectoryStream(path);
                            for (Path file : dir) {
                                OFALoadTree treeNode = new OFALoadTree(file);
                                String fileExtension = fileOperation.getExtension(treeNode.getValue());
                                String fileName = fileOperation.getFileName(treeNode.getValue());
                                if (fileExtension == null || fileExtension.equals(".py") || fileExtension.equals(".ospk") || fileExtension.equals(".topo") || fileExtension.equals(".params") || fileExtension.equals(".log") || fileExtension.equals(".rpt") || fileExtension.equals(".session")) {
                                    if (fileExtension == null) {
                                        treeNode.setExpanded(true);
                                        source.getChildren().add(treeNode);
                                    } else {
                                        if (fileExtension.matches(".(ospk|params|topo|py|log|rpt|session)")) {
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
