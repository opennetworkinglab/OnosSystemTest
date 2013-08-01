package tai_ofa;

import com.sun.org.apache.xerces.internal.parsers.IntegratedParserConfiguration;
import java.awt.TextArea;
import java.util.ArrayList;
import java.util.Locale;
import javafx.event.EventHandler;
import javafx.scene.Group;
import javafx.scene.Node;
import javafx.scene.control.Button;
import javafx.scene.control.ContextMenu;
import javafx.scene.control.MenuItem;
import javafx.scene.control.Tab;
import javafx.scene.input.MouseEvent;
import javafx.scene.layout.StackPane;
import javafx.scene.web.PopupFeatures;
import javafx.scene.web.WebEngine;
import javafx.scene.web.WebView;
import javafx.util.Callback;
import javax.swing.JOptionPane;


/*
 * To change this template, choose Tools | Templates and open the template in
 * the editor.
 */
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

 * /**
 */
public class CodeEditorParams extends StackPane {

    TAI_OFA OFAReference;
    WebView webview = new WebView();
    private String editingCode;
    ContextMenu contextMenu;
    TAILocale label = new TAILocale(new Locale("en", "EN"));
    String editorScriptsPath = label.OFAHarnessPath;
    private final String editingTemplate =
            "<!doctype html>"
            + "<html>"
            + "<head>"
            + " <link rel=\"stylesheet\"href=\"file://editorScriptPath/codemirror.css\">".replace("editorScriptPath", editorScriptsPath+"/EditorScripts")
            + "  <script src=\"file://editorScriptPath/codemirror.js\"></script>".replace("editorScriptPath", editorScriptsPath+"/EditorScripts")
            + "  <script src=\"file://editorScriptPath/foldcode.js\"></script>".replace("editorScriptPath", editorScriptsPath+"/EditorScripts")
            + "  <script src=\"file://editorScriptPath/perl.js\"></script>".replace("editorScriptPath", editorScriptsPath+"/EditorScripts")
            + "  <script src=\"file://editorScriptPath/xml.js\"></script>".replace("editorScriptPath", editorScriptsPath+"/EditorScripts")
            + " <style type=\"text/css\">"
            + "</style>"
            + "</head>"
            + "<body>"
            + "<form><textarea id=\"code\" name=\"code\">\n"
            + "${code}"
            + "</textarea></form>"
            + "<script>"
            + " var foldFunc = CodeMirror.newFoldFunction(CodeMirror.tagRangeFinder);"
            + "var editor;"
            + "editor = CodeMirror.fromTextArea(document.getElementById(\"code\"), {"
            + "mode: \"perl\","
            + "     lineNumbers: true,"
            + "onGutterClick: foldFunc,"
            + "extraKeys: {\"Ctrl-Q\" : function(cm){foldFunc(cm, cm.getCursor().line);}}"
            + "  });"
            + "</script>"
            + "</body>"
            + "</html>";

    /**
     * applies the editing template to the editing code to create the
     * html+javascript source for a code editor.
     */
    private String applyEditingTemplate() {
        editingTemplate.replace("${code}", editingCode);        
        return editingTemplate.replace("${code}", editingCode);
    }

    public void setOFA(TAI_OFA reference) {
        OFAReference = reference;
    }

    /**
     * sets the current code in the editor and creates an editing snapshot of
     * the code which can be reverted to.
     */
    public void setCode(String newCode) {
        this.editingCode = newCode;
        webview.getEngine().loadContent(applyEditingTemplate());
    }

    public String getCurrentLine() {
        return (String) webview.getEngine().executeScript("editor.getLine(editor.getCursor().line);");
    }

    public String getCurrentLineNumber() {
        return webview.getEngine().executeScript("editor.getLineNumber(editor.getCursor().line);").toString();

    }

    public String getCurrentLine(int lineNumber) {
        Integer lines = lineNumber;
        return (String) webview.getEngine().executeScript("editor.getLine(line);".replace("line", lines.toString()));

    }

    /**
     * returns the current code in the editor and updates an editing snapshot of
     * the code which can be reverted to.
     */
    public String getCodeAndSnapshot() {
        this.editingCode = (String) webview.getEngine().executeScript("editor.getValue();");
        return editingCode;
    }

    public void alert() {
        webview.getEngine().executeScript("editor.myFunction();");
    }

    public int cursorPosfromTop() {
        return (Integer) webview.getEngine().executeScript("editor.cursorTopPos();");
    }

    public int cursorPosfromLeft() {
        return (Integer) webview.getEngine().executeScript("editor.cursorLeftPos();");
    }

    public void clearMarker(String line) {
        int lineNumber = Integer.parseInt(line) - 1;
        String lineNumberString = "editor.clearMarker(clearGutter);".replace("clearGutter", String.valueOf(lineNumber));
        webview.getEngine().executeScript(lineNumberString);
    }

    public void SetError(String line, final String errorType) {

        final String tooltip = "editor.setMarker(line-1, \"<a id='error' title='errorType \"  +  \"'><img src='file://editorScriptPath/Delete.png'/></a>%N%\"); ".replace("editorScriptPath", editorScriptsPath+"/EditorScripts");
        Integer lineCount = (Integer) webview.getEngine().executeScript("editor.lineCount();");
        int i;
        for (i = 1; i <= lineCount; i++) {
            String tooltipToExcute = tooltip.replace("line", line).replace("errorType", errorType);
            if (!"".equals(errorType)) {
                webview.getEngine().executeScript(tooltipToExcute);
            }
        }

    }

    public void SetWarning(String line, final String errorType) {

        final String tooltip = "editor.setMarker(line-1, \"<a id='error' title='errorType \"  +  \"'><img src='file://editorScriptPath/Warning.png'/></a>%N%\"); ".replace("editorScriptPath", editorScriptsPath+"/EditorScripts");
        Integer lineCount = (Integer) webview.getEngine().executeScript("editor.lineCount();");
        int i;
        for (i = 1; i <= lineCount; i++) {
            String tooltipToExcute = tooltip.replace("line", line).replace("errorType", errorType);
            if (!"".equals(errorType)) {
                webview.getEngine().executeScript(tooltipToExcute);
            }
        }

    }

    public void SetInfo(String line, final String errorType) {

        final String tooltip = "editor.setMarker(line-1, \"<a id='error' title='errorType \"  +  \"'><img src='file://editorScriptPath/info.jpg'/></a>%N%\"); ".replace("editorScriptPath", editorScriptsPath+"/EditorScripts");
        Integer lineCount = (Integer) webview.getEngine().executeScript("editor.lineCount();");
        int i;
        for (i = 1; i <= lineCount; i++) {
            String tooltipToExcute = tooltip.replace("line", line).replace("errorType", errorType);
            if (!"".equals(errorType)) {
                webview.getEngine().executeScript(tooltipToExcute);
            }
        }

    }

    /**
     * revert edits of the code to the last edit snapshot taken.
     */
    public void revertEdits() {
        setCode(editingCode);
    }

    CodeEditorParams(String editingCode) {
        this.editingCode = editingCode;
        webview.getEngine().loadContent(applyEditingTemplate());
        this.getChildren().add(webview);
    }

    public void contextMenu() {
        contextMenu = new ContextMenu();
        MenuItem myMenuItem = new MenuItem();
        contextMenu.getItems().add(myMenuItem);
    }
}
