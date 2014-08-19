#!/usr/bin/python
# -*- coding: utf-8 -*-

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
        Or Ctrl+2, then "f"

Script inspired by: http://bear330.wordpress.com/

"""

# ===============================================================================
# Pydev Extensions in Jython code protocol
# ===============================================================================

if False:
    from org.python.pydev.editor import PyEdit  # @UnresolvedImport
    cmd = 'command string'
    editor = PyEdit
    systemGlobals = {}

assert cmd is not None
assert editor is not None

if cmd == 'onCreateActions':

    from org.python.pydev.editor.actions import PyAction  # @UnresolvedImport

    from org.eclipse.swt.widgets import Display  # @UnresolvedImport

    from java.io import FileWriter  # @UnresolvedImport

    import java.lang.Exception  # @UnresolvedImport
    from java.lang import Runnable  # @UnresolvedImport

    FORMAT_ACTION_DEFINITION_ID = \
        'org.python.pydev.editor.actions.pyFormatStd'
    FORMAT_ACTION_ID = \
        'org.python.pydev.editor.actions.navigation.pyFormatStd'

    FormatterLogger = systemGlobals.get('FormatterLogger')
    if FormatterLogger is None:
        
        class FormatterLogger(object):
            '''
            We can't let this Formatter's trace into our main log.
            Let's just print it out into stdout.
            '''

            def __init__(self, fileName):
                self._fileName = fileName

            def _log(self, level, msg):
                import datetime
                now = datetime.datetime.now()
                print '{date} - Formatter:{level} - {fileName} - {msg}'.\
                    format(date=now.strftime('%Y-%m-%d %H:%M'
                                             ), level=level, fileName=self._fileName,
                           msg=msg)

            def debug(self, msg):
                self._log('DEBUG', msg)

            def info(self, msg):
                self._log('INFO', msg)

            def warn(self, msg):
                self._log('WARNING', msg)

            def error(self, msg):
                self._log('ERROR', msg)

        systemGlobals['FormatterLogger'] = FormatterLogger

    logger = FormatterLogger(editor.getEditorFile().getName())

    PythonTidyAction = systemGlobals.get("PythonTidyAction")
    if PythonTidyAction is None:
        class PythonTidyAction(PyAction):

            def __init__(self, editor):
                PyAction.__init__(self)
                self._editor = editor

            @staticmethod
            def autopep8_cmd(f):  # @NoSelf
                return 'autopep8 -a -a -a --in-place --experimental --max-line-length 100 "{f}"'.format(
                    f=str(f))

            @staticmethod
            def docformatter_cmd(f):  # @NoSelf
                return 'docformatter --in-place --pre-summary-newline "{f}"'.format(
                    f=str(f))

            @staticmethod
            def apply_formatting(source_file, fileName, logger):  # @NoSelf
                """Applies formatting on the input source_file with file name =
                fileName (from editor)"""
                import subprocess
                f = source_file
                final_formatting_cmd = '({autopep8}) && ({docformatter})'.format(
                    autopep8=PythonTidyAction.autopep8_cmd(f),
                    docformatter=PythonTidyAction.docformatter_cmd(f))
                logger.info('Will be running $' + final_formatting_cmd)
                exec_frame = subprocess.Popen(
                    final_formatting_cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
                (cstdout, cstderr) = exec_frame.communicate()
                if cstderr:
                    logger.error(cstderr)
                if cstdout:
                    logger.info(cstdout)
                logger.info(
                    'Formatting for {fileName} complete with return_code:{rt}'.format(
                        fileName=fileName,
                        rt=exec_frame.returncode))

            def run(self):
                import tempfile
                import os
                import traceback

                logger = FormatterLogger(
                    self._editor.getEditorFile().getName())

                try:
                    # PySelection(editor)
                    ps = self._editor.createPySelection()
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

                        logger.warn(
                            'Format selected text is not supported yet.')
                        tmp_src_fileWriter.write('')

                        # A kind of solution is to insert a special comment in
                        # front and end of selection text, pythontidy it, and
                        # extract text according that comment.

                    tmp_src_fileWriter.close()

                    PythonTidyAction.apply_formatting(
                        tmp_src,
                        self._editor.getEditorFile().getName(), logger)

                    resulting_file = open(tmp_src, 'r')
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
                    if startLine >= doc.getNumberOfLines():
                        startLine = doc.getNumberOfLines() - 1
                    self._editor.selectAndReveal(
                        doc.getLineOffset(startLine),
                        0)

                except java.lang.Exception as e:
                    self.beep(e)
                    logger.error(traceback.format_exc())
                except:
                    logger.error(traceback.format_exc())
        systemGlobals["PythonTidyAction"] = PythonTidyAction

    def bindInInterface():
        act = PythonTidyAction(editor)

        act.setActionDefinitionId(FORMAT_ACTION_DEFINITION_ID)
        act.setId(FORMAT_ACTION_ID)
        try:
            editor.setAction(FORMAT_ACTION_ID, act)
        except:
            logger.error('Binding failed')

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

    logger.info('Binding formatter')

    # register Ctrl Shift F
    # comment the line below to deactivate ctrl+shift+f shortcut
    runInUi(bindInInterface)

    # Change these constants if the default does not suit your needs
    ACTIVATION_STRING = 'f'
    WAIT_FOR_ENTER = False

    # Register the extension as an ActionListener.
    editor.addOfflineActionListener(
        ACTIVATION_STRING,
        PythonTidyAction(editor),
        'Format with autopep8 and docformatter',
        WAIT_FOR_ENTER)
    logger.info('Binding successful!!!! ')
    