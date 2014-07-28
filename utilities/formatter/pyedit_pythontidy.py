"""
TSE Eclipse Formatter Jython script.

Requires:
    autopep8,     --$ pip install autopep8
    docformatter, --$ pip install docformatter

To enable: Window -> Preferences -> PyDev (expanded) -> Scripting PyDev:
    1) check both "Show ..." checkboxes
    2) browse to folder containing this script
    3) Apply and OK!
    4) View log on PyDev Scripting Console (it automatically starts a low priority console)
    5) Now you can Ctrl+Shift+f to format away!

Script inspired by: http://bear330.wordpress.com/

"""
# ===============================================================================
# Pydev Extensions in Jython code protocol
# ===============================================================================

if False:
    from org.python.pydev.editor import PyEdit  # @UnresolvedImport
    cmd = 'command string'
    editor = PyEdit

assert cmd is not None
assert editor is not None

if cmd == 'onCreateActions':
    # from org.eclipse.jface.action import Action
    from org.python.pydev.editor.actions import PyAction  # @UnresolvedImport
    from org.python.pydev.core.docutils import PySelection  # @UnresolvedImport
    from java.lang import Runnable  # @UnresolvedImport
    from org.eclipse.swt.widgets import Display  # @UnresolvedImport
    from org.eclipse.jface.text import IDocument  # @UnresolvedImport
    from org.eclipse.jface.text import TextSelection  # @UnresolvedImport

    from java.io import FileWriter  # @UnresolvedImport
    import java.lang.Exception  # @UnresolvedImport

    FORMAT_ACTION_DEFINITION_ID = "org.python.pydev.editor.actions.pyFormatStd"
    FORMAT_ACTION_ID = "org.python.pydev.editor.actions.navigation.pyFormatStd"

    def autopep8_cmd(f):
        return 'autopep8 -a -a -a --in-place --experimental "{f}"'.format(
            f=str(f))

    def docformatter_cmd(f):
        return 'docformatter --in-place --pre-summary-newline "{f}"'.format(
            f=str(f))

    def apply_formatting(source_file, fileName):
        """Applies formatting on the input source_file with file name =
        fileName (from editor)"""

        import subprocess
        f = source_file
        final_formatting_cmd = '({autopep8}) && ({docformatter})'.format(
            autopep8=autopep8_cmd(f),
            docformatter=docformatter_cmd(f))
        print 'Formatter:INFO: Will be running $' + final_formatting_cmd
        exec_frame = subprocess.Popen(
            final_formatting_cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        (cstdout, cstderr) = exec_frame.communicate()
        if cstderr:
            print 'Formatter:ERROR:' + cstderr
        if cstdout:
            print 'Formatter:INFO:' + cstdout
        print 'Formatter:INFO: Formatting for {fileName} complete with return_code:{rt}'.\
            format(fileName=fileName, rt=exec_frame.returncode)

    class PythonTidyAction(PyAction):

        def __init__(self, *args, **kws):
            PyAction.__init__(self, *args, **kws)

        def run(self):
            import tempfile
            import os
            import traceback

            try:
                ps = editor.createPySelection()  # PySelection(editor)
                doc = ps.getDoc()
                startLine = ps.getStartLineIndex()

                tmp_src = tempfile.mktemp()
                tmp_src_fileWriter = FileWriter(tmp_src)

                formatAll = False
                if ps.getTextSelection().getLength() == 0:
                    # format all.
                    c = doc.get()
                    tmp_src_fileWriter.write(c)
                    formatAll = True
                else:
                    # format selection.
                    # c = ps.getSelectedText()
                    # tmp_src_fileWriter.write(ps.getSelectedText())
                    print "Format selected text is not supported yet."
                    tmp_src_fileWriter.write("")
                    # A kind of solution is to insert a special comment in
                    # front and end of selection text, pythontidy it, and
                    # extract text according that comment.

                tmp_src_fileWriter.close()

                apply_formatting(tmp_src, editor.getEditorFile().getName())

                resulting_file = open(tmp_src, "r")
                result = resulting_file.read()
                resulting_file.close()

                os.remove(tmp_src)

                if startLine >= doc.getNumberOfLines():
                    startLine = doc.getNumberOfLines() - 1

                if formatAll:
                    doc.set(result)
                else:
                    # doc.replace(doc.getLineOffset(startLine), 0, result)
                    pass

                # sel = TextSelection(doc, doc.getLineOffset(startLine), 0)
                # self.getTextEditor()#.getSelectionProvider().setSelection(sel)
            except java.lang.Exception as e:
                self.beep(e)
                print traceback.format_exc()
            except:
                print traceback.format_exc()

    def bindInInterface():
        act = PythonTidyAction()

        act.setActionDefinitionId(FORMAT_ACTION_DEFINITION_ID)
        act.setId(FORMAT_ACTION_ID)
        try:
            editor.setAction(FORMAT_ACTION_ID, act)
        except:
            pass

    class RunInUi(Runnable):

        """
        Helper class that implements a Runnable (just so that we can pass it to
        the Java side).

        It simply calls some callable.

        """

        def __init__(self, c):
            self.callable = c

        def run(self):
            self.callable()

    def runInUi(callAble):
        """@param callable: the callable that will be run in the UI."""
        Display.getDefault().asyncExec(RunInUi(callAble))
    print "Formatter:INFO:Binding formatter"
    runInUi(bindInInterface)
    print "Formatter:INFO:Binded "
