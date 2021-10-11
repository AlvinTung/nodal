from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *

import os
import sys
import uuid
import random

FONT_SIZES = [7, 8, 9, 10, 11, 12, 13, 14, 18, 24, 36, 48, 64, 72, 96, 144, 288]
IMAGE_EXTENSIONS = ['.jpg','.png','.bmp']
HTML_EXTENSIONS = ['.htm', '.html']

def hexuuid():
    return uuid.uuid4().hex

def splitext(p):
    return os.path.splitext(p)[1].lower()

class TextEdit(QTextEdit):
    def render_new_screen(self, a):
        self.clear()
                  
        textPos = 0

        for i in range(len(a)):

#            cursor = self.textCursor()
#            cursor.setPosition(textPos)
#            self.setTextCursor(cursor)
            cursor = self.textCursor()
            cursor.insertFragment(a[i])    
            
            if(i != len(a) - 1):
                self.setFontUnderline(False)
                self.insertPlainText(" ")
#                cursor = self.textCursor()
#                # set cursor to the beginning of the text
#                textPos = textPos + 1
#                cursor.setPosition(textPos)
#                self.setTextCursor(cursor)
        
    def getTextAsArray(self):
         # position in text
         i = 0
         blocks = []
         newBlock = False

         startPosition = 0
         endPosition = 0
         start = False 

         # get the current cursor
         cursor = self.textCursor()
         # set cursor to the beginning of the text 
         cursor.setPosition(0)
         self.setTextCursor(cursor)
         cursor = self.textCursor()
    
         while(self.document().characterAt(i) != '\0'):
             # get the current cursor
             cursor = self.textCursor()
             # set cursor to the beginning of the text
             cursor.setPosition(i + 1)
             self.setTextCursor(cursor)
             cursor = self.textCursor()

             if(cursor.charFormat().fontUnderline() is True):
                 newBlock = True
             else:
                 newBlock = False

             if(self.document().characterAt(i) != ' ' and newBlock is False):
                 # set the start position
                 if(start is False):
                     startPosition = i
                     start = True
                
             elif(self.document().characterAt(i) != ' ' and newBlock is True):
                 if(start is False):
                    startPosition = i
                    start = True 
         
             elif(self.document().characterAt(i) == ' ' and newBlock is True):
                 print("IOOOP")

             elif(self.document().characterAt(i) == ' ' and newBlock is False): 
                 endPosition = i

                 cursor.setPosition(startPosition, QTextCursor.MoveAnchor);
                 cursor.setPosition(endPosition, QTextCursor.KeepAnchor);

                 blocks.append(cursor.selection())
                 start = False

             if(self.document().characterAt(i + 1) == '\0' and start is True):
                 endPosition = i
                 
                 cursor.setPosition(startPosition, QTextCursor.MoveAnchor);
                 cursor.setPosition(endPosition, QTextCursor.KeepAnchor);
               
                 blocks.append(cursor.selection())
                 start = False               
             i = i + 1 

         return blocks

    def canInsertFromMimeData(self, source):

        if source.hasImage():
            return True
        else:
            return super(TextEdit, self).canInsertFromMimeData(source)

    def insertFromMimeData(self, source):

        cursor = self.textCursor()
        document = self.document()

        if source.hasUrls():

            for u in source.urls():
                file_ext = splitext(str(u.toLocalFile()))
                if u.isLocalFile() and file_ext in IMAGE_EXTENSIONS:
                    image = QImage(u.toLocalFile())
                    document.addResource(QTextDocument.ImageResource, u, image)
                    cursor.insertImage(u.toLocalFile())

                else:
                    # If we hit a non-image or non-local URL break the loop and fall out
                    # to the super call & let Qt handle it
                    break

            else:
                # If all were valid images, finish here.
                return


        elif source.hasImage():
            image = source.imageData()
            uuid = hexuuid()
            document.addResource(QTextDocument.ImageResource, uuid, image)
            cursor.insertImage(uuid)
            return

        super(TextEdit, self).insertFromMimeData(source)


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        layout = QVBoxLayout()
        self.editor = TextEdit()
        # Setup the QTextEdit editor configuration
        self.editor.setAutoFormatting(QTextEdit.AutoAll)
        self.editor.selectionChanged.connect(self.update_format)
        # Initialize default font size.
        font = QFont('Times', 12)
        self.editor.setFont(font)
        # We need to repeat the size to init the current format.
        self.editor.setFontPointSize(12)

        # self.path holds the path of the currently open file.
        # If none, we haven't got a file open yet (or creating new).
        self.path = None

        layout.addWidget(self.editor)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # Uncomment to disable native menubar on Mac
        # self.menuBar().setNativeMenuBar(False)

        switch_toolbar = QToolBar("Switch")
        switch_toolbar.setIconSize(QSize(16,16))
        self.addToolBar(switch_toolbar)

        switch_to_node_action = QAction(QIcon(os.path.join('images', 'node.png')), "Nodal View...", self)
        switch_to_node_action.setStatusTip("Nodal View")
        switch_to_node_action.triggered.connect(self.switch_to_node)

        switch_toolbar.addAction(switch_to_node_action)

        switch_to_unmeaning_action = QAction(QIcon(os.path.join('images', 'unmeaning.png')), "Unmeaning View...", self)
        switch_to_unmeaning_action.setStatusTip("Unmeaning View")
        switch_to_unmeaning_action.triggered.connect(self.switch_to_unmeaning)

        switch_toolbar.addAction(switch_to_unmeaning_action) 

        mutate_toolbar = QToolBar("Mutate")
        mutate_toolbar.setIconSize(QSize(16,16))
        self.addToolBar(mutate_toolbar) 

        randomise_text_action = QAction(QIcon(os.path.join('images', 'randomise.png')), "Randomise Text...", self)
        randomise_text_action.setStatusTip("Randomise Text")
        randomise_text_action.triggered.connect(self.randomise_text)
        
        mutate_toolbar.addAction(randomise_text_action)

        add_to_databaseU_action = QAction(QIcon(os.path.join('images', 'u.png')), "Add to U", self)
        add_to_databaseU_action.triggered.connect(self.add_to_databaseU)

        get_random_databaseU_action = QAction(QIcon(os.path.join('images', 'u.png')), "Get U", self)
        get_random_databaseU_action.triggered.connect(self.get_random_databaseU)
        get_random_databaseU_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_U)) 

        mutate_toolbar.addAction(get_random_databaseU_action)

        file_toolbar = QToolBar("File")
        file_toolbar.setIconSize(QSize(14, 14))
        self.addToolBar(file_toolbar)
        file_menu = self.menuBar().addMenu("&File")

        open_file_action = QAction(QIcon(os.path.join('images', 'blue-folder-open-document.png')), "Open file...", self)
        open_file_action.setStatusTip("Open file")
        open_file_action.triggered.connect(self.file_open)
        file_menu.addAction(open_file_action)
        file_toolbar.addAction(open_file_action)

        save_file_action = QAction(QIcon(os.path.join('images', 'disk.png')), "Save", self)
        save_file_action.setStatusTip("Save current page")
        save_file_action.triggered.connect(self.file_save)
        file_menu.addAction(save_file_action)
        file_toolbar.addAction(save_file_action)

        saveas_file_action = QAction(QIcon(os.path.join('images', 'disk--pencil.png')), "Save As...", self)
        saveas_file_action.setStatusTip("Save current page to specified file")
        saveas_file_action.triggered.connect(self.file_saveas)
        file_menu.addAction(saveas_file_action)
        file_toolbar.addAction(saveas_file_action)

        print_action = QAction(QIcon(os.path.join('images', 'printer.png')), "Print...", self)
        print_action.setStatusTip("Print current page")
        print_action.triggered.connect(self.file_print)
        file_menu.addAction(print_action)
        file_toolbar.addAction(print_action)

        edit_toolbar = QToolBar("Edit")
        edit_toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(edit_toolbar)
        edit_menu = self.menuBar().addMenu("&Edit")

        undo_action = QAction(QIcon(os.path.join('images', 'arrow-curve-180-left.png')), "Undo", self)
        undo_action.setStatusTip("Undo last change")
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction(QIcon(os.path.join('images', 'arrow-curve.png')), "Redo", self)
        redo_action.setStatusTip("Redo last change")
        redo_action.triggered.connect(self.editor.redo)
        edit_toolbar.addAction(redo_action)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        cut_action = QAction(QIcon(os.path.join('images', 'scissors.png')), "Cut", self)
        cut_action.setStatusTip("Cut selected text")
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self.editor.cut)
        edit_toolbar.addAction(cut_action)
        edit_menu.addAction(cut_action)

        copy_action = QAction(QIcon(os.path.join('images', 'document-copy.png')), "Copy", self)
        copy_action.setStatusTip("Copy selected text")
        cut_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.editor.copy)
        edit_toolbar.addAction(copy_action)
        edit_menu.addAction(copy_action)

        paste_action = QAction(QIcon(os.path.join('images', 'clipboard-paste-document-text.png')), "Paste", self)
        paste_action.setStatusTip("Paste from clipboard")
        cut_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.editor.paste)
        edit_toolbar.addAction(paste_action)
        edit_menu.addAction(paste_action)

        select_action = QAction(QIcon(os.path.join('images', 'selection-input.png')), "Select all", self)
        select_action.setStatusTip("Select all text")
        cut_action.setShortcut(QKeySequence.SelectAll)
        select_action.triggered.connect(self.editor.selectAll)
        edit_menu.addAction(select_action)

        edit_menu.addSeparator()

        wrap_action = QAction(QIcon(os.path.join('images', 'arrow-continue.png')), "Wrap text to window", self)
        wrap_action.setStatusTip("Toggle wrap text to window")
        wrap_action.setCheckable(True)
        wrap_action.setChecked(True)
        wrap_action.triggered.connect(self.edit_toggle_wrap)
        edit_menu.addAction(wrap_action)

        format_toolbar = QToolBar("Format")
        format_toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(format_toolbar)
        format_menu = self.menuBar().addMenu("&Format")

        # We need references to these actions/settings to update as selection changes, so attach to self.
        self.fonts = QFontComboBox()
        self.fonts.currentFontChanged.connect(self.editor.setCurrentFont)
        format_toolbar.addWidget(self.fonts)

        self.fontsize = QComboBox()
        self.fontsize.addItems([str(s) for s in FONT_SIZES])

        # Connect to the signal producing the text of the current selection. Convert the string to float
        # and set as the pointsize. We could also use the index + retrieve from FONT_SIZES.
        self.fontsize.currentIndexChanged[str].connect(lambda s: self.editor.setFontPointSize(float(s)) )
        format_toolbar.addWidget(self.fontsize)

        self.bold_action = QAction(QIcon(os.path.join('images', 'edit-bold.png')), "Bold", self)
        self.bold_action.setStatusTip("Bold")
        self.bold_action.setShortcut(QKeySequence.Bold)
        self.bold_action.setCheckable(True)
        self.bold_action.toggled.connect(lambda x: self.editor.setFontWeight(QFont.Bold if x else QFont.Normal))
        format_toolbar.addAction(self.bold_action)
        format_menu.addAction(self.bold_action)

        self.italic_action = QAction(QIcon(os.path.join('images', 'edit-italic.png')), "Italic", self)
        self.italic_action.setStatusTip("Italic")
        self.italic_action.setShortcut(QKeySequence.Italic)
        self.italic_action.setCheckable(True)
        self.italic_action.toggled.connect(self.editor.setFontItalic)
        format_toolbar.addAction(self.italic_action)
        format_menu.addAction(self.italic_action)

        self.underline_action = QAction(QIcon(os.path.join('images', 'edit-underline.png')), "Underline", self)
        self.underline_action.setStatusTip("Underline")
        self.underline_action.setShortcut(QKeySequence.Underline)
        self.underline_action.setCheckable(True)
        self.underline_action.toggled.connect(self.editor.setFontUnderline)
        format_toolbar.addAction(self.underline_action)
        format_menu.addAction(self.underline_action)

        format_menu.addSeparator()

        self.alignl_action = QAction(QIcon(os.path.join('images', 'edit-alignment.png')), "Align left", self)
        self.alignl_action.setStatusTip("Align text left")
        self.alignl_action.setCheckable(True)
        self.alignl_action.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignLeft))
        format_toolbar.addAction(self.alignl_action)
        format_menu.addAction(self.alignl_action)

        self.alignc_action = QAction(QIcon(os.path.join('images', 'edit-alignment-center.png')), "Align center", self)
        self.alignc_action.setStatusTip("Align text center")
        self.alignc_action.setCheckable(True)
        self.alignc_action.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignCenter))
        format_toolbar.addAction(self.alignc_action)
        format_menu.addAction(self.alignc_action)

        self.alignr_action = QAction(QIcon(os.path.join('images', 'edit-alignment-right.png')), "Align right", self)
        self.alignr_action.setStatusTip("Align text right")
        self.alignr_action.setCheckable(True)
        self.alignr_action.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignRight))
        format_toolbar.addAction(self.alignr_action)
        format_menu.addAction(self.alignr_action)

        self.alignj_action = QAction(QIcon(os.path.join('images', 'edit-alignment-justify.png')), "Justify", self)
        self.alignj_action.setStatusTip("Justify text")
        self.alignj_action.setCheckable(True)
        self.alignj_action.triggered.connect(lambda: self.editor.setAlignment(Qt.AlignJustify))
        format_toolbar.addAction(self.alignj_action)
        format_menu.addAction(self.alignj_action)

        format_group = QActionGroup(self)
        format_group.setExclusive(True)
        format_group.addAction(self.alignl_action)
        format_group.addAction(self.alignc_action)
        format_group.addAction(self.alignr_action)
        format_group.addAction(self.alignj_action)

        format_menu.addSeparator()

        switch_menu = self.menuBar().addMenu("&Switch")
        switch_menu.addAction(switch_to_node_action)
        switch_menu.addAction(switch_to_unmeaning_action)

        mutate_menu = self.menuBar().addMenu("&Mutate")
        mutate_menu.addAction(randomise_text_action)
        mutate_menu.addAction(add_to_databaseU_action)
        mutate_menu.addAction(get_random_databaseU_action)

        # A list of all format-related widgets/actions, so we can disable/enable signals when updating.
        self._format_actions = [
            self.fonts,
            self.fontsize,
            self.bold_action,
            self.italic_action,
            self.underline_action,
            # We don't need to disable signals for alignment, as they are paragraph-wide.
        ]

        # Initialize.
        self.update_format()
        self.update_title()
        self.show()

    def block_signals(self, objects, b):
        for o in objects:
            o.blockSignals(b)

    def update_format(self):
        """
        Update the font format toolbar/actions when a new text selection is made. This is neccessary to keep
        toolbars/etc. in sync with the current edit state.
        :return:
        """
        # Disable signals for all format widgets, so changing values here does not trigger further formatting.
        self.block_signals(self._format_actions, True)

        self.fonts.setCurrentFont(self.editor.currentFont())
        # Nasty, but we get the font-size as a float but want it was an int
        self.fontsize.setCurrentText(str(int(self.editor.fontPointSize())))

        self.italic_action.setChecked(self.editor.fontItalic())
        self.underline_action.setChecked(self.editor.fontUnderline())
        self.bold_action.setChecked(self.editor.fontWeight() == QFont.Bold)

        self.alignl_action.setChecked(self.editor.alignment() == Qt.AlignLeft)
        self.alignc_action.setChecked(self.editor.alignment() == Qt.AlignCenter)
        self.alignr_action.setChecked(self.editor.alignment() == Qt.AlignRight)
        self.alignj_action.setChecked(self.editor.alignment() == Qt.AlignJustify)

        self.block_signals(self._format_actions, False)

    def dialog_critical(self, s):
        dlg = QMessageBox(self)
        dlg.setText(s)
        dlg.setIcon(QMessageBox.Critical)
        dlg.show()

    def file_open(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "", "HTML documents (*.html);Text documents (*.txt);All files (*.*)")

        try:
            with open(path, 'rU') as f:
                text = f.read()

        except Exception as e:
            self.dialog_critical(str(e))

        else:
            self.path = path
            # Qt will automatically try and guess the format as txt/html
            self.editor.setText(text)
            self.update_title()

    def generate_node_source(self):
        textedit = self.editor
        t = textedit.textCursor()
 
        DIRA = '/Volumes/Untitled/nodal/sourcea/'
        no_of_files = len([name for name in os.listdir(DIRA) if os.path.isfile(os.path.join(DIRA, name))])

        print("YUP")
        print(str(no_of_files))
        random_file = random.randint(0, no_of_files - 2)
        print("fuck")
        print(str(random_file))

        f = open(DIRA + "s" + str(random_file) + ".txt", "r")
        u = f.readlines()
        for y in range(len(u)):
            u_bound = len(u[y]) - 1
            s = u[y][0:u_bound]
            t.insertText(s)
            t.insertText("\n")

        DIRB = '/Volumes/Untitled/nodal/sourceb/'
        no_of_files = len([name for name in os.listdir(DIRB) if os.path.isfile(os.path.join(DIRB, name))])

        print("YUP")
        print(str(no_of_files))
        random_file = random.randint(0, no_of_files - 2)

        f = open(DIRB + "s" + str(random_file) + ".txt", "r")
        u = f.readlines()
        for y in range(len(u)):
            u_bound = len(u[y]) - 1
            s = u[y][0:u_bound]
            t.insertText(s)
            t.insertText("\n")

    def switch_to_node(self):
        textedit = self.editor
        t = textedit.textCursor()
        allText = textedit.toPlainText()

        if(len(allText) == 0):
            self.generate_node_source()
        else:
            filepath = 'output.txt'
            # open file in read mode
            with open(filepath, 'r') as read_obj:
                # read first character
                one_char = read_obj.read(1)
                # if not fetched then file is empty
                if one_char == "\0" or one_char == "\n":
                    f = open(filepath, "w")
                    f.write(allText)
                    f.close()
                else:
                    f = open(filepath, "a")
                    f.write(" ")
                    f.write(allText)
                    f.close()

            textedit.clear()

            self.generate_node_source() 

    def switch_to_unmeaning(self):
        textedit = self.editor
        t = textedit.textCursor()
        allText = textedit.toPlainText()

        if(len(allText) == 0):
            print("HASSAN")
        else:
            a = self.editor.getTextAsArray()

            for x in range(len(a)):
                if(" " in a[x].toPlainText()):
                    filepath = 'output.txt'
                    # open file in read mode
                    with open(filepath, 'r') as read_obj:
                        # read first character
                        one_char = read_obj.read(1)
                        # if not fetched then file is empty
                        if one_char == "\0" or one_char == "\n":
                            f = open(filepath, "w")
                            f.write(a[x].toPlainText())
                            f.close()
                        else:
                            f = open(filepath, "a")
                            f.write(" ")
                            f.write(a[x].toPlainText())
                            f.close()

            textedit.clear()
            

    def add_to_databaseU(self):
        textedit = self.editor
        t = textedit.textCursor()
        input = t.selectedText()

        filepath = 'u.txt'
        # open file in read mode
        with open(filepath, 'r') as read_obj:
            # read first character
            one_char = read_obj.read(1)
            # if not fetched then file is empty
            if one_char == "\0" or one_char == "\n":
                f = open(filepath, "w")
                f.write(input)
                f.close()
            else:
                f = open(filepath, "a")
                f.write("\n")
                f.write(input)
                f.close()

    def get_random_databaseU(self):
        textedit = self.editor
        t = textedit.textCursor()

        f = open("u.txt", "r")
        u = f.readlines()
        rnd_line = random.choice(u)
        u_bound = len(rnd_line)

        if("\n" in rnd_line):
            s = rnd_line[0:u_bound - 1]
        else: 
            s = rnd_line[0:u_bound]

        t.insertText(s)

    def randomise_text(self):
        textedit = self.editor
        textdoc = textedit.document()

        t = textedit.textCursor()

        a = self.editor.getTextAsArray()
     
        random.shuffle(a)
  
        self.editor.render_new_screen(a)
        cursor = textedit.textCursor()
        cursor.setPosition(0)
        textedit.setTextCursor(cursor)


    def file_save(self):
        if self.path is None:
            # If we do not have a path, we need to use Save As.
            return self.file_saveas()

        text = self.editor.toHtml() if splitext(self.path) in HTML_EXTENSIONS else self.editor.toPlainText()

        try:
            with open(self.path, 'w') as f:
                f.write(text)

        except Exception as e:
            self.dialog_critical(str(e))

    def file_saveas(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save file", "", "HTML documents (*.html);Text documents (*.txt);All files (*.*)")

        if not path:
            # If dialog is cancelled, will return ''
            return

        text = self.editor.toHtml() if splitext(path) in HTML_EXTENSIONS else self.editor.toPlainText()

        try:
            with open(path, 'w') as f:
                f.write(text)

        except Exception as e:
            self.dialog_critical(str(e))

        else:
            self.path = path
            self.update_title()

    def file_print(self):
        dlg = QPrintDialog()
        if dlg.exec_():
            self.editor.print_(dlg.printer())

    def update_title(self):
        self.setWindowTitle("%s - Nodal" % (os.path.basename(self.path) if self.path else "Untitled"))

    def edit_toggle_wrap(self):
        self.editor.setLineWrapMode( 1 if self.editor.lineWrapMode() == 0 else 0 )


if __name__ == '__main__':
    def clean_database(fname):
        filepath = fname
        # open file in read mode
        with open(filepath, 'r') as read_obj:
            # read first character
            one_char = read_obj.read(1)
            # if not fetched then file is empty
            if one_char == "\0" or one_char == "\n":
                print("empty file")
            else:
                print("cleaning...")
                f = open(filepath, "r")
                l = f.readlines()

                for i in l:
                    if(i == "\n"):
                        l.remove("\n")

                f.close()
                f = open(filepath, "w")

                for i in range(len(l)):
                   f.write(l[i])

                f.close()

    def clean():
        clean_database("u.txt")

    app = QApplication(sys.argv)
    app.setApplicationName("Nodal")
    clean()
    window = MainWindow()
    app.exec_()
