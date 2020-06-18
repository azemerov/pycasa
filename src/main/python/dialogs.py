from PyQt5.QtWidgets import QPushButton, QDialog, QWidget, QLabel, QGridLayout, QLineEdit, QApplication
import sys

class MyDialog(QDialog):
    def __init__(self, parent, caption, **kwargs):
        super(MyDialog, self).__init__(parent)
        self.caption = caption
        self.kwargs = kwargs
        self.entries = {}
        self.result = {}
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        self.setLayout(layout)
        self.setModal(True)

        layout.setColumnStretch(1, 4)
        layout.setColumnStretch(2, 4)
        row = 0
        for n,v in self.kwargs.items():
            label = QLabel('%s:'%n)
            layout.addWidget(label, row, 0)
            edt = QLineEdit(self)
            edt.setText(v)
            layout.addWidget(edt, row, 1)
            self.entries[n] = edt
            row += 1
        ok = QPushButton('OK')
        ok.clicked.connect(self.onOkBtn)
        layout.addWidget(ok, row, 0)
        cancel = QPushButton('Cancel')
        cancel.clicked.connect(self.onCancelBtn)
        layout.addWidget(cancel, row, 1)
        self.result = {}

    def onOkBtn(self):
        for n,edt in self.entries.items():
            self.result[n] = edt.text()
        self.close()

    def onCancelBtn(self):
        self.result = {}
        self.close()

    def run(self):
        self.exec_()
        return self.result

def makeEdit(parent, layout, caption, value, row, editedHandler=None):
    label = QLabel(caption)
    layout.addWidget(label, row, 0)
    result = QLineEdit(parent)
    result.setText(str(value))
    layout.addWidget(result, row, 1)
    if editedHandler:
        result.textEdited.connect(editedHandler)
    return result

def makeButton(parent, layout, caption, clicked, row, col):
    result = QPushButton(caption)
    result.clicked.connect(clicked)
    layout.addWidget(result, row, col)
    return result

def makeOkCancelButtons(parent, layout, clicked1, clicked2, row):
    return makeButton(parent, layout, '&Ok', clicked1, row, 0),\
           makeButton(parent, layout, '&Cancel', clicked2, row, 1)

class BrightnessConstrastFrame(QWidget):
    def __init__(self, parent, brightness, contrast, onclose, onbrightness, oncontrast):
        super(BrightnessConstrastFrame, self).__init__(parent)
        layout = QGridLayout()
        # layout.setColumnStretch(1, 4)
        # layout.setColumnStretch(2, 4)
        self.brightnessEdt = makeEdit(self, layout, 'Brightness:', brightness, 0, onbrightness)
        self.contrastEdt = makeEdit(self, layout, 'Contrast:', contrast, 1, oncontrast)
        makeOkCancelButtons(self, layout, self.onOkBtn, self.onCancelBtn, 2)
        self.setLayout(layout)
        self.onclose = onclose

    def onOkBtn(self):
        self.close()
        QApplication.processEvents()
        self.onclose((float(self.brightnessEdt.text()), float(self.contrastEdt.text())))

    def onCancelBtn(self):
        self.close()
        QApplication.processEvents()
        self.onclose(None)

class ConstrastFrame(QWidget):
    def __init__(self, parent, contrast, onclose):
        super(ConstrastFrame, self).__init__(parent)
        layout = QGridLayout()
        # layout.setColumnStretch(1, 4)
        # layout.setColumnStretch(2, 4)
        self.contrastEdt = makeEdit(self, layout, 'Contrast:', contrast, 1)
        makeOkCancelButtons(self, layout, self.onOkBtn, self.onCancelBtn, 2)
        self.setLayout(layout)
        self.onclose = onclose

    def onOkBtn(self):
        self.close()
        QApplication.processEvents()
        self.onclose(float(self.contrastEdt.text()))

    def onCancelBtn(self):
        self.close()
        QApplication.processEvents()
        self.onclose(None)

class NumValFrame(QWidget):
    def __init__(self, parent, name, value, onclose):
        super(NumValFrame, self).__init__(parent)
        layout = QGridLayout()
        # layout.setColumnStretch(1, 4)
        # layout.setColumnStretch(2, 4)
        self.edt = makeEdit(self, layout, name, value, 1)
        makeOkCancelButtons(self, layout, self.onOkBtn, self.onCancelBtn, 2)
        self.setLayout(layout)
        self.onclose = onclose

    def onOkBtn(self):
        self.close()
        QApplication.processEvents()
        self.onclose(float(self.edt.text()))

    def onCancelBtn(self):
        self.close()
        QApplication.processEvents()
        self.onclose(None)

class OrtonFrame(QWidget):
    #d = EntriesDialog(win.master, "Orthon effect", (("Main image brightness:","1.1"),
    # ("Blured image brightness:","1.3"), ("Blured image zoom:","1.01"), ("Blend alpha:","0.3"),))
    def __init__(self, parent, brightness, brightness2, zoom, alpha, onclose):
        #super(OrtonFrame, self).__init__(parent)
        super().__init__(parent)
        layout = QGridLayout()
        # layout.setColumnStretch(1, 4)
        # layout.setColumnStretch(2, 4)
        self.brightnessEdt = makeEdit(self, layout, 'Main image brightness:', brightness, 0)
        self.brightness2Edt = makeEdit(self, layout, 'Blured image brightness:', brightness2, 1)
        self.zoomEdt = makeEdit(self, layout, 'Blured image zoom:', zoom, 2)
        self.alphaEdt = makeEdit(self, layout, 'Blend alpha:', alpha, 3)
        makeOkCancelButtons(self, layout, self.onOkBtn, self.onCancelBtn, 4)
        self.setLayout(layout)
        self.onclose = onclose

    def onOkBtn(self):
        self.close()
        QApplication.processEvents()
        self.onclose((
            float(self.brightnessEdt.text()),
            float(self.brightness2Edt.text()),
            float(self.zoomEdt.text()),
            float(self.alphaEdt.text())
        ))

    def onCancelBtn(self):
        self.close()
        QApplication.processEvents()
        self.onclose(None)


if __name__ == '__main__':
    from fbs_runtime.application_context.PyQt5 import ApplicationContext
    appctxt = ApplicationContext()
    appctxt.app.setStyle('Fusion')
    #w = MyDialog(None, one='1',two='2')
    w = MyDialog(None, 'test', **{'one':'1','two':'2'})
    w.show() # real app should call w.run() which returns result dictionary
    exit_code = appctxt.app.exec_()
    for n,v in w.result.items():
        print(n,v)
    sys.exit(exit_code)