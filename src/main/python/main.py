from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QLabel, \
    QScrollArea, QFileSystemModel, QTreeView, QGroupBox, QApplication, QSplitter, \
    QLayout, QStyle, QSizePolicy, QAction
#QMessageBox, QDirModel, QMenuBar, QGridLayout, QFrame,QBoxLayout,
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtCore import Qt, QDir, QRect, QPoint, QSize, QSortFilterProxyModel #QEvent,
from PyQt5.Qt import pyqtSignal
import sys
import os
import time
import threading
import PIL.Image
#from PIL.ImageQt import ImageQt

class ImagePopup(QLabel):
    """
    The ImagePopup class is a QLabel that displays a popup, zoomed image
    on top of another label.
    Taken from http://www.intransitione.com/blog/pyqt-playground-image-gallery-with-zoom/
    """
    def __init__(self, parent):
        #super(QLabel, self).__init__(parent)
        super().__init__()

        # set pixmap and size, which is the double of the original pixmap
        thumb = parent.orig # parent.pixmap()
        # imageSize = thumb.size()
        # imageSize.setWidth(imageSize.width()*2)
        # imageSize.setHeight(imageSize.height()*2)
        #self.setPixmap(thumb.scaled(imageSize,Qt.KeepAspectRatioByExpanding))
        self.setPixmap(thumb.scaled(120,120,Qt.KeepAspectRatioByExpanding))

        # center the zoomed image on the thumb
        position = self.cursor().pos()
        print('popup, pos=%s'%position)
        #position.setX(position.x() - thumb.size().width())
        #position.setY(position.y() - thumb.size().height())
        self.move(position)

        # FramelessWindowHint may not work on some window managers on Linux
        # so I force also the flag X11BypassWindowManagerHint
        self.setWindowFlags(Qt.Popup | Qt.WindowStaysOnTopHint
                            | Qt.FramelessWindowHint
                            | Qt.X11BypassWindowManagerHint)

    def leaveEvent(self, event):
        """ When the mouse leave this widget, destroy it.
        :param event:
        """
        self.destroy()

class ImageLabel(QLabel):
    """ This widget displays an ImagePopup when the mouse enters its region
    Taken from http://www.intransitione.com/blog/pyqt-playground-image-gallery-with-zoom/
    """
    def __init__(self, parent):
        #super(QLabel, self).__init__(parent)
        _ = parent
        super().__init__()
        self.p = None

    def enterEvent(self, event):
        self.p = ImagePopup(self)
        self.p.show()
        event.accept()


class ClickableLabel(QLabel):

    clicked = pyqtSignal()

    def __init__(self, dname, fname):
        super().__init__(fname)
        self.fileName = os.path.join(dname, fname)
        self.clicked.connect(self.onDblClick)
        self.lastTs = None

    def showImage(self):
        if not self.pixmap():
            orig = QPixmap(self.fileName)
            pixmap = orig.scaled(60,60, Qt.KeepAspectRatioByExpanding)
            self.setPixmap(pixmap) #button.setIcon(QIcon(pixmap))
            #label.clicked.connect(self.onFileDblClick)
            #label.installEventFilter(self)
            #label.orig = orig
            # label.clicked.connect(
            #     lambda: self.viewWindow.showImage(os.path.join(dname, fname)))

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        if self.lastTs and time.time()-self.lastTs < 0.4:
            self.clicked.emit()
        self.lastTs = time.time()

    def onDblClick(self):
        mainWindow.viewWindow.showImage(self.fileName)

def imgFiles(dirName):
    return (fn for fn in os.listdir(dirName) if fn.lower().endswith('.jpg'))

class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=-1, hspacing=-1, vspacing=-1):
        super(FlowLayout, self).__init__(parent)
        self._hspacing = hspacing
        self._vspacing = vspacing
        self._items = []
        self.setContentsMargins(margin, margin, margin, margin)

    def __del__(self):
        del self._items[:]

    def addItem(self, item):
        self._items.append(item)

    def horizontalSpacing(self):
        if self._hspacing >= 0:
            return self._hspacing
        else:
            return self.smartSpacing(
                QStyle.PM_LayoutHorizontalSpacing)

    def verticalSpacing(self):
        if self._vspacing >= 0:
            return self._vspacing
        else:
            return self.smartSpacing(
                QStyle.PM_LayoutVerticalSpacing)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)

    def expandingDirections(self):
        return Qt.Orientations(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        left, top, right, bottom = self.getContentsMargins()
        size += QSize(left + right, top + bottom)
        return size

    def doLayout(self, rect, testonly):
        left, top, right, bottom = self.getContentsMargins()
        effective = rect.adjusted(+left, +top, -right, -bottom)
        x = effective.x()
        y = effective.y()
        lineheight = 0
        for item in self._items:
            widget = item.widget()
            hspace = self.horizontalSpacing()
            if hspace == -1:
                hspace = widget.style().layoutSpacing(
                    QSizePolicy.PushButton,
                    QSizePolicy.PushButton, Qt.Horizontal)
            vspace = self.verticalSpacing()
            if vspace == -1:
                vspace = widget.style().layoutSpacing(
                    QSizePolicy.PushButton,
                    QSizePolicy.PushButton, Qt.Vertical)
            nextX = x + item.sizeHint().width() + hspace
            if nextX - hspace > effective.right() and lineheight > 0:
                x = effective.x()
                y = y + lineheight + vspace
                nextX = x + item.sizeHint().width() + hspace
                lineheight = 0
            if not testonly:
                item.setGeometry(
                    QRect(QPoint(x, y), item.sizeHint()))
            x = nextX
            lineheight = max(lineheight, item.sizeHint().height())
        return y + lineheight - rect.y() + bottom

    def smartSpacing(self, pm):
        parent = self.parent()
        if parent is None:
            return -1
        elif parent.isWidgetType():
            return parent.style().pixelMetric(pm, None, parent)
        else:
            return parent.spacing()

from dialogs import MyDialog

def test(v):
    print(v)
    result = MyDialog(None, 'test', **{'one':'1','two':'2'}).run()
    for n,v in result.items():
        print(n,v)

def test1():
    print('test1')

def doExit():
    appctxt.app.quit()

menueDef = [
    ('&File', (
        ('&New', QIcon('exit.png'), lambda: test('New'), None, None),
        ('&Old', QIcon('exit.png'), lambda: test('Old'), None, None),
        ('&Exit', QIcon('exit.png'), doExit, 'Ctrl+Q', 'Exit application'),
    ),
    ),
    ('&Edit', (
        # ('&Del', QIcon('exit.png'), lambda: test('Del'), None, None),
        # ('&Ins', QIcon('exit.png'), lambda: test('Ins'), None, None),
    ),),
]

import transforms

def makeMenu(bar, menues, obj):
    for menu in menues:
        _menu = bar.addMenu(menu[0])
        for item in menu[1]:
            act = QAction(item[1], item[0], obj)
            act.triggered.connect(item[2])
            if item[3]: act.setShortcut(item[3])
            if item[4]: act.setStatusTip(item[4])
            _menu.addAction(act)

        if menu[0]=='&Edit':
            for item in transforms.getTransforms():
                if item[1]:
                    act = QAction(item[1], item[0], obj)
                else:
                    act = QAction(item[0], obj)
                act.triggered.connect(item[2])
                if item[3]: act.setShortcut(item[3])
                if item[4]: act.setStatusTip(item[4])
                _menu.addAction(act)



mainWindow = None
class MyWindow(QMainWindow): # QWidget

    def __init__(self):
        #super(MyWindow, self).__init__()
        super().__init__()
        global mainWindow
        mainWindow = self
        self.orig = None
        self.fileLabels = []
        self.model = None
        self.tree = None
        self.grpBox = None
        self.viewWindow = None
        self._drawIndex = -1
        self.initUI()

    def initUI(self):
        self.resize(600, 800)

        bar = self.menuBar()
        makeMenu(bar, menueDef, self)

        #self.model = QDirModel([], QDir.Dirs, QDir.NoSort )
        rootPath = 'C:/Users/azemero' # QDir.currentPath()
        self.model = QFileSystemModel()
        self.model.setRootPath(rootPath)
        self.model.setFilter(QDir.AllDirs|QDir.NoDotAndDotDot)
        #todo: filter or custom tree
        proxyModel = QSortFilterProxyModel()
        proxyModel.setSourceModel(self.model)
        proxyModel.setFilterRegExp(r"^([^.]+)$")

        self.tree = QTreeView()
        self.tree.setModel(proxyModel)
        self.tree.setColumnHidden(1, True)
        self.tree.setColumnHidden(2, True)
        self.tree.setColumnHidden(3, True)
        self.tree.doubleClicked.connect(self.onDirDblClick)
        self.tree.selectionModel().selectionChanged.connect(self.onDirSelChange)

        self.tree.setSortingEnabled(True)
        self.tree.sortByColumn(0, Qt.AscendingOrder)
        idx = self.model.index(rootPath)
        idx = proxyModel.mapFromSource(idx)
        self.tree.setRootIndex(idx)

        self.tree.setAnimated(False)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)

        self.tree.setWindowTitle("Dir View")
        #self.tree.resize(640, 480)
        self.tree.setMinimumWidth(200)

        windowLayout = QHBoxLayout()
        windowLayout.setSpacing(0) #windowLayout.setContentsMargins(0,0,0,0)
        windowLayout.addWidget(self.tree, alignment=Qt.AlignLeft)

        #left.addWidget(self.tree)

        self.grpBox = QGroupBox('')
        self.grpBox.setLayout(FlowLayout()) #self.grpBox.setLayout(QGridLayout(self))
        self.grpBox.setMinimumWidth(400)
        windowLayout.addWidget(self.grpBox) #, alignment=Qt.AlignLeft)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.tree)
        splitter.addWidget(self.grpBox)
        splitter.setSizes([200, 800])
#        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        windowLayout.addWidget(splitter)

        #~self.setLayout(windowLayout)
        center  = QWidget()
        center.setLayout(windowLayout)
        self.setCentralWidget(center)

        self.viewWindow = ViewWindow()

    def onDirDblClick(self, signal):
        file_path=self.tree.model().filePath(signal)
        #print(file_path)
        if os.path.isdir(file_path):
            fnames = imgFiles(file_path)
            self.drawFiles(file_path, fnames)

    def onDirSelChange(self, newitem, olditem):
        _ = olditem
        idx = newitem.indexes()[0]
        idx = self.tree.model().mapToSource(idx)
        file_path=self.model.filePath(idx)

        #print(file_path)
        if os.path.isdir(file_path):
            fnames = imgFiles(file_path)
            self.drawFiles(file_path, fnames)

    # def onFileDblClick(self):
    #     self.viewWindow.openImage('')
    #     self.viewWindow.show()

    # def eventFilter(self, obj, event):
    #     if event.type() == QEvent.MouseButtonPress:
    #         pass #здесь выполняем код
    #     return True

    def drawFiles(self, dname, fnames):
        row = col = 0
        #print('drawFiles.1')
        for label in self.fileLabels:
            label.setParent(None) # remove old image labels
        del self.fileLabels[:]
        QApplication.processEvents()
        #print('drawFiles.2')

        for fname in fnames:
            label = ClickableLabel(dname, fname) # QLabel(fname) # ImageLabel(fname)
            #label.showImage()
            self.fileLabels.append(label)
            #self.grpBox.layout().addWidget(label, row, col)
            self.grpBox.layout().addWidget(label)
            col +=1
            if col % 6 == 0:
                row += 1
                col = 0
        #print('drawFiles.3')
        QApplication.processEvents()
        self._drawIndex = 0 if fnames else -1
        threading.Thread(target=self.drawFile).start()
        #print('drawFiles.4')

    def drawFile(self):
        if self._drawIndex < len(self.fileLabels):
            self.fileLabels[self._drawIndex].showImage()
            #print('drawFile')
            QApplication.processEvents()
        self._drawIndex += 1
        if self._drawIndex >= len(self.fileLabels):
            self._drawIndex = -1
        else:
            threading.Thread(target=self.drawFile).start()

def pil2pixmap(im):
    """
    from https://stackoverflow.com/questions/34697559/pil-image-to-qpixmap-conversion-issue
    :param im: instance of PIL.Image
    """
    if im.mode == "RGB":
        r, g, b = im.split()
        im = PIL.Image.merge("RGB", (b, g, r))
    elif  im.mode == "RGBA":
        r, g, b, a = im.split()
        im = PIL.Image.merge("RGBA", (b, g, r, a))
    elif im.mode == "L":
        im = im.convert("RGBA")
    im2 = im.convert("RGBA")
    data = im2.tobytes("raw", "RGBA")
    qim = QImage(data, im.size[0], im.size[1], QImage.Format_ARGB32)
    pixmap = QPixmap.fromImage(qim)
    return pixmap

class ViewWindow(QMainWindow): # QWidget):
    def __init__(self):
        super().__init__()
        self.pilorig = None
        self.orig = None
        self.scroll = None
        self.label = None
        self.controlPanel = None
        self.dirName, self.fileName = '', ''
        self.dirFileNames = []
        self.fileIdx = -1
        self.grpBox = None
        self.initUI()

    def initUI(self):
        #self.resize(250, 150)
        self.setWindowTitle("PyQT Tuts!")
        transforms.editWindow = self

        bar = self.menuBar()
        makeMenu(bar, menueDef, self)

        layout1 = QVBoxLayout()

        self.scroll = QScrollArea()
        layout1.addWidget(self.scroll)

        self.label = QLabel()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.label)

        #window.resize(pixmap.width(),pixmap.height())

        self.grpBox = QGroupBox('')
        layout2 = QHBoxLayout()
        prevButton = QPushButton('&Prev')
        prevButton.clicked.connect(self.onPrevBtn)
        nextButton = QPushButton('&Next')
        nextButton.clicked.connect(self.onNextBtn)
        layout2.addWidget(prevButton)
        layout2.addWidget(nextButton)
        self.grpBox.setLayout(layout2)

        layout1.addWidget(self.grpBox)
        panel = QWidget(self)
        self.controlPanel = QHBoxLayout()
        panel.setLayout(self.controlPanel)
        layout1.addWidget(panel)

        center = QWidget()
        center.setLayout(layout1)
        self.setCentralWidget(center)

    def resizeEvent(self, event):
        QWidget.resizeEvent(self, event)
        self.sizeImage()

    def openImage(self, fileName):
        self.setWindowTitle(fileName)
        self.dirName = os.path.dirname(fileName)
        self.fileName = os.path.basename(fileName)
        self.dirFileNames = list(imgFiles(self.dirName))
        self.fileIdx = self.dirFileNames.index(self.fileName)
        if fileName:
            #self.orig = QPixmap(fileName)
            self.pilorig = PIL.Image.open(fileName) #QPixmap(fileName)
            self.orig = pil2pixmap(self.pilorig) #QPixmap.fromImage(qimg)
            #self.label.setPixmap(self.orig)
            self.sizeImage()

    def fullFileName(self):
        if self.fileName:
            return os.path.join(self.dirName, self.fileName)
        else:
            return None


    def showImage(self, fileName):
        self.openImage(fileName)
        self.show()

    def updateImage(self, pilImage):
        self.pilorig = pilImage
        self.orig = pil2pixmap(pilImage)
        self.sizeImage() #update_img(img, True, label='Equalize', operation=do_equalize, params=None)

    def sizeImage(self):
        if self.orig:
            pixmap = self.orig.scaled(self.scroll.width(), self.scroll.height(),
                                      Qt.KeepAspectRatio,
                                      transformMode = Qt.SmoothTransformation)
            self.label.setPixmap(pixmap)

    def nextFileName(self):
        if self.fileIdx < len(self.dirFileNames)-1:
            return os.path.join(self.dirName, self.dirFileNames[self.fileIdx+1])
        else:
            return None

    def prevFileName(self):
        if self.fileIdx > 0:
            return os.path.join(self.dirName, self.dirFileNames[self.fileIdx-1])
        else:
            return None

    def onNextBtn(self):
        fn  = self.nextFileName()
        if fn:
            self.openImage(os.path.join(self.dirName, fn))

    #@staticmethod
    def onPrevBtn(self):
        # alert = QMessageBox()
        # alert.setText('You clicked the button!')
        # alert.exec_()
        fn = self.prevFileName()
        if fn:
            self.openImage(os.path.join(self.dirName, fn))


if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    appctxt.app.setStyle('Fusion')
    #appctxt.app.setStyleSheet("QPushButton { margin: 10ex; }")
    MyWindow().show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)