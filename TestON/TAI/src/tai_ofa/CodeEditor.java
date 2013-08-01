package tai_ofa;

import java.util.Locale;
import javafx.scene.layout.StackPane;
import javafx.scene.web.WebView;
import javax.print.Doc;
import javax.swing.tree.DefaultTreeCellEditor;
import org.w3c.dom.Document;
import org.w3c.dom.Element;

/*
	
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

public class CodeEditor extends StackPane {

    /**
     * a webview used to encapsulate the JavaScript.
     */
    final WebView webview = new WebView();
    /**
     * a snapshot of the code to be edited kept for easy initialization and
     * reversion of editable code.
     */
    private String editingCode;
    /**
     * a template for editing code - this can be changed to any template derived
     * from the supported modes at java to allow syntax highlighted editing of a
     * wide variety of languages.
     */
    TAILocale label = new TAILocale(new Locale("en", "EN"));
    String editorScriptsPath = label.OFAHarnessPath;
    private final String editingTemplate =
            "<!doctype html>"
            + "<html>"
            + "<head>"
            + " <link rel=\"stylesheet\" href=\"file://editorScriptPath/codemirror.css\">".replace("editorScriptPath", editorScriptsPath + "/EditorScripts")
            + "  <script src=\"file://editorScriptPath/codemirror.js\"></script>".replace("editorScriptPath", editorScriptsPath + "/EditorScripts")
            + "  <script src=\"file://editorScriptPath/clike.js\"></script>".replace("editorScriptPath", editorScriptsPath + "/EditorScripts")
            + "  <script src=\"file://editorScriptPath/javascript-hint.js\"></script>".replace("editorScriptPath", editorScriptsPath + "/EditorScripts")
            + "  <script src=\"file://editorScriptPath/search.js\"></script>".replace("editorScriptPath", editorScriptsPath + "/EditorScripts")
            + "  <script src=\"file://editorScriptPath/dialog.js\"></script>".replace("editorScriptPath", editorScriptsPath + "/EditorScripts")
            + "  <script src=\"file://editorScriptPath/searchcursor.js\"></script>".replace("editorScriptPath", editorScriptsPath + "/EditorScripts")
            + "  <script src=\"file://editorScriptPath/simple-hint.js\"></script>".replace("editorScriptPath", editorScriptsPath + "/EditorScripts")
            + " <link rel=\"stylesheet\" href=\"file://editorScriptPath/simple-hint.css\">".replace("editorScriptPath", editorScriptsPath + "/EditorScripts")
            + "  <script src=\"file://editorScriptPath/javascript-hint.js\"></script>".replace("editorScriptPath", editorScriptsPath + "/EditorScripts")
            + "  <script src=\"file://editorScriptPath/foldcode.js\"></script>".replace("editorScriptPath", editorScriptsPath + "/EditorScripts")
            + "  <script src=\"file://editorScriptPath/perl.js\"></script>".replace("editorScriptPath", editorScriptsPath + "/EditorScripts")
            + "  <script src=\"file://editorScriptPath/xml.js\"></script>".replace("editorScriptPath", editorScriptsPath + "/EditorScripts")
            + "</head>"
            + "<body>"
            + "<form><textarea id=\"code\" name=\"code\">\n"
            + "${code}"
            + "</textarea></form>"
            + "<script>"
            + "var editor;"
            + "editor = CodeMirror.fromTextArea(document.getElementById(\"code\"), {"
            + "mode: \"perl\","
            + "lineNumbers: true,"
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

    /**
     * sets the current code in the editor and creates an editing snapshot of
     * the code which can be reverted to.
     */
    public void setCode(String newCode) {
        this.editingCode = newCode;
        webview.getEngine().loadContent(applyEditingTemplate());

        // webview.getStylesheets().add("eclipse.css");
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

    public void setLine(int lineNumber, String text) {
        String lineToSet = "editor.setLine(" + lineNumber + ",'lineText');";
        webview.getEngine().executeScript(lineToSet.replace("lineText", text));
    }

    /**
     * returns the current code in the editor and updates an editing snapshot of
     * the code which can be reverted to.
     */
    public String getCodeAndSnapshot() {
        //Document doc = webview.getEngine().getDocument();
//            Element el = doc.getElementById("code");
        webview.getEngine().executeScript("editor.refresh();");
        this.editingCode = (String) webview.getEngine().executeScript("editor.getValue();");

        return editingCode;
    }

    public int cursorPosfromTop() {
        return (Integer) webview.getEngine().executeScript("editor.cursorTopPos();");

    }

    public int cursorPosfromLeft() {
        return (Integer) webview.getEngine().executeScript("editor.cursorLeftPos();");

    }

    public String test() {
        return (String) webview.getEngine().executeScript("editor.find();");

    }

    public void clearMarker(String line) {
        int lineNumber = Integer.parseInt(line) - 1;
        String lineNumberString = "editor.clearMarker(clearGutter);".replace("clearGutter", String.valueOf(lineNumber));
        webview.getEngine().executeScript(lineNumberString);
    }

    public void SetError(String line, final String errorType) {

        final String tooltip = "editor.setMarker(line-1, \"<a id='error' title='errorType \"  +  \"'><img src='file://editorScriptPath/Delete.png'/></a>%N%\"); ".replace("editorScriptPath", editorScriptsPath + "/EditorScripts");
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

        final String tooltip = "editor.setMarker(line-1, \"<a id='error' title='errorType \"  +  \"'><img src='file://editorScriptPath/Warning.png'/></a>%N%\"); ".replace("editorScriptPath", editorScriptsPath + "/EditorScripts");
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

        final String tooltip = "editor.setMarker(line-1, \"<a id='error' title='errorType \"  +  \"'><img src='file://editorScriptPath/info.jpg'/></a>%N%\"); ".replace("editorScriptPath", editorScriptsPath + "/EditorScripts");
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

    /**
     * Create a new code editor.
     *
     * @param editingCode the initial code to be edited in the code editor.
     */
    CodeEditor(String editingCode) {
        this.editingCode = editingCode;

        // webview.setPrefSize(650, 325);
        //  webview.setMinSize(150, 325);
        webview.getEngine().loadContent(applyEditingTemplate());


        this.getChildren().add(webview);
    }
}
