from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QLabel, \
    QScrollArea, QFileSystemModel, QTreeView, QGroupBox, QApplication, QSplitter, \
    QLayout, QStyle, QSizePolicy, QAction, QGraphicsView, QGraphicsScene, QFileDialog
#QMessageBox, QDirModel, QMenuBar, QGridLayout, QFrame,QBoxLayout,
from PyQt5.QtGui import QIcon, QPixmap, QImage, QPainter, QPen, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QDir, QRect, QPoint, QSize, QSortFilterProxyModel, QEvent, QModelIndex, \
    QFile, QDataStream, QIODevice, QByteArray
from PyQt5.Qt import pyqtSignal
import sys
import os
import time
import threading
import PIL.Image
#from PIL.ImageQt import ImageQt
import pickle

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
            base = os.path.basename(self.fileName)
            pixmap = mainWindow.thumbs.get(base)
            if not pixmap:
                orig = QPixmap(self.fileName)
                pixmap = orig.scaled(60,60, Qt.KeepAspectRatioByExpanding)
                mainWindow.thumbs[base] = pixmap
                mainWindow.newImgFound = True
                print('new file %s is found'%base)
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

FILE_MENU = [
    ('&File', (
        #('&Save', QIcon(), doSaveFile, None, None),
        ('&Exit', QIcon('exit.png'), doExit, 'Ctrl+Q', 'Exit application'),
        ),
    ),
    ('&Edit', (
        # ('&Del', QIcon('exit.png'), lambda: test('Del'), None, None),
        # ('&Ins', QIcon('exit.png'), lambda: test('Ins'), None, None),
        ),
    ),
    ('&View', tuple(),
    ),
]

import transforms

def addAction(menu, owner, caption, func, shortcut, tip):
    act = QAction(caption, owner)
    act.triggered.connect(func)
    if shortcut: act.setShortcut(shortcut)
    if tip: act.setStatusTip(tip)
    menu.addAction(act)
    return act

def makeMenu(bar, menues, obj):
    for menu in menues:
        _menu = bar.addMenu(menu[0])
        for item in menu[1]:
            addAction(_menu, obj, item[0], item[2], item[3], item[4]) # item[1] (Icon is ignored, todo: add support)

def serializeDict(dictionary):
    # QPixmap is not pickable so let's transform it into QByteArray that does support pickle
    state = []
    for key, value in dictionary.items():
        qbyte_array = QByteArray()
        stream = QDataStream(qbyte_array, QIODevice.WriteOnly)
        stream << value
        state.append((key, qbyte_array))
    return state

def deserializeDict(array):
    result = {}
    # retrieve a QByteArray and transform it into QPixmap
    for (key, buffer) in array:
        qpixmap = QPixmap()
        stream = QDataStream(buffer, QIODevice.ReadOnly)
        stream >> qpixmap
        result[key] = qpixmap
    return result



mainWindow = None
class MyWindow(QMainWindow): # QWidget

    def __init__(self):
        #super(MyWindow, self).__init__()
        super().__init__()
        global mainWindow
        mainWindow = self
        self.fileLabels = []
        self.model = None
        self.tree = None
        self.grpBox = None
        self.viewWindow = None
        self._drawIndex = -1
        self.thumbs = {}
        self.thumbFileName = None
        self.newImgFound = False # if True, new image file non-referenced in .pythumbs file is found, need to update the .pythumbs file
        self.initUI()

    def initUI(self):
        self.resize(600, 800)

        bar = self.menuBar()
        makeMenu(bar, FILE_MENU, self)

        # #self.model = QDirModel([], QDir.Dirs, QDir.NoSort )
        # rootPath = 'C:/Users/azemero' # QDir.currentPath()
        # self.model = QFileSystemModel()
        # self.model.setRootPath(rootPath)
        # self.model.setFilter(QDir.AllDirs|QDir.NoDotAndDotDot)
        # #todo: filter or custom tree
        # proxyModel = QSortFilterProxyModel()
        # proxyModel.setSourceModel(self.model)
        # proxyModel.setFilterRegExp(r"^([^.]+)$")
        #
        # self.tree = QTreeView()
        # self.tree.setModel(proxyModel)
        # self.tree.setColumnHidden(1, True)
        # self.tree.setColumnHidden(2, True)
        # self.tree.setColumnHidden(3, True)
        # self.tree.doubleClicked.connect(self.onDirDblClick)
        # self.tree.selectionModel().selectionChanged.connect(self.onDirSelChange)
        #
        # self.tree.setSortingEnabled(True)
        # self.tree.sortByColumn(0, Qt.AscendingOrder)
        # idx = self.model.index(rootPath)
        # idx = proxyModel.mapFromSource(idx)
        # self.tree.setRootIndex(idx)
        #
        # self.tree.setAnimated(False)
        # self.tree.setIndentation(20)
        # self.tree.setSortingEnabled(True)
        #
        # self.tree.setWindowTitle("Dir View")
        # #self.tree.resize(640, 480)
        # self.tree.setMinimumWidth(200)

        self.model = QStandardItemModel()
        parentItem = self.model.invisibleRootItem()
        frstIdx = None
        for i in range(4):
            item = QStandardItem("Pictures %d" % i)
            item.setData('C:/Users/azemero/Pictures')
            #item.setIcon(QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__),'..','icons','base','24.png'))))
            item.setIcon(QIcon(appctxt.get_resource('folder_png8773.ico')))
            parentItem.appendRow(item)
            if not frstIdx:
                frstIdx = item.index()
            #parentItem = item
        self.model.setHeaderData(0, Qt.Horizontal, "Directories")
        self.tree = QTreeView(self)
        self.tree.setModel(self.model)
        self.tree.clicked[QModelIndex].connect(self.onTreeClick)
        self.tree.setMinimumWidth(200)

        windowLayout = QHBoxLayout()
        windowLayout.setSpacing(0) #windowLayout.setContentsMargins(0,0,0,0)
        windowLayout.addWidget(self.tree, alignment=Qt.AlignLeft)

        self.grpBox = QGroupBox('')
        self.grpBox.setLayout(FlowLayout()) #self.grpBox.setLayout(QGridLayout(self))
        self.grpBox.setMinimumWidth(400)
        windowLayout.addWidget(self.grpBox) #, alignment=Qt.AlignLeft)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.tree)
        splitter.addWidget(self.grpBox)
        splitter.setSizes([200, 800])
        splitter.setStretchFactor(1, 1)

        windowLayout.addWidget(splitter)

        #~self.setLayout(windowLayout)
        center  = QWidget()
        center.setLayout(windowLayout)
        self.setCentralWidget(center)

        self.viewWindow = ViewWindow()
        if frstIdx:
            self.onTreeClick(frstIdx)

    def onDirDblClick(self, signal):
        file_path=self.tree.model().filePath(signal)
        #print(file_path)
        if os.path.isdir(file_path):
            self.drawFiles(file_path)

    def onTreeClick(self, index):
        item = self.model.itemFromIndex(index)
        file_path = item.data()
        #print(file_path)
        if os.path.isdir(file_path):
            self.drawFiles(file_path)

    # def onDirSelChange(self, newitem, olditem):
    #     _ = olditem
    #     idx = newitem.indexes()[0]
    #     idx = self.tree.model().mapToSource(idx)
    #     file_path=self.model.filePath(idx)
    #     #print(file_path)
    #     if os.path.isdir(file_path):
    #         self.drawFiles(file_path)

    # def onFileDblClick(self):
    #     self.viewWindow.openImage('')
    #     self.viewWindow.show()

    # def eventFilter(self, obj, event):
    #     if event.type() == QEvent.MouseButtonPress:
    #         pass #здесь выполняем код
    #     return True

    def drawFiles(self, dname):
        row = col = 0
        for label in self.fileLabels:
            label.setParent(None) # remove old image labels
        del self.fileLabels[:]
        QApplication.processEvents()

        self.thumbFileName = os.path.join(dname, '.pythumbs')
        self.newImgFound = False
        if os.path.isfile(self.thumbFileName):
            with open(self.thumbFileName, 'rb') as f:
                data = pickle.load(f)
                self.thumbs = deserializeDict(data)
        else:
            self.thumbs = {}

        fnames = imgFiles(dname)
        for fname in fnames:
            label = ClickableLabel(dname, fname)
            self.fileLabels.append(label)
            self.grpBox.layout().addWidget(label)
            col +=1
            if col % 6 == 0:
                row += 1
                col = 0
        #print('drawFiles.3')
        QApplication.processEvents()
        self._drawIndex = 0 if fnames else -1
        threading.Thread(target=self.drawFile).start()

    def drawFile(self):
        if self._drawIndex < len(self.fileLabels):
            self.fileLabels[self._drawIndex].showImage()
            QApplication.processEvents()
        self._drawIndex += 1
        if self._drawIndex >= len(self.fileLabels):
            self._drawIndex = -1
            if self.thumbFileName and self.newImgFound:
                print('update .pythumbs')
                array = serializeDict(self.thumbs)
                with open(self.thumbFileName, 'wb') as f:
                    pickle.dump(array, f)
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
        self.savedImg = None
        self.controlPanel = None
        self.dirName, self.fileName = '', ''
        self.dirFileNames = []
        self.fileIdx = -1
        self.ctrl = None # transformation control widget
        self.locator = None # locator rectangle widget
        self.locator1 = None # locator 1st point
        self.locator2 = None # locator 2nd point
        self.scale = (1,1)
        self.show_histogram = False
        # usage of QGraphicsScene and QGraphicsView is taken from
        # https://stackoverflow.com/questions/50851587/undo-functionality-for-qpainter-drawellipse-function
        self.gv = None
        self.scene = None
        self.scaledPixmap = None
        self.histogram = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("PyQT Tuts!")
        transforms.editWindow = self

        bar = self.menuBar()
        makeMenu(bar, FILE_MENU, self)
        menu = bar.actions()[2].menu()
        menu.addSeparator()
        addAction(menu, self, 'Show &Histogram', self.toggleHistogram, 'Ctrl+H', 'Show/hide histogram')

        menu = bar.actions()[1].menu()
        menu.addSeparator()
        for item in transforms.getTransforms():
            addAction(menu, self, item[0], item[2], item[3], item[4]) # item[1] (Icon is ignored, todo: add support)

        menu = bar.actions()[0].menu()
        menu.addSeparator()
        addAction(menu, self, '&Next', self.onNextBtn, 'Ctrl+N', 'Next image')
        addAction(menu, self, '&Prev', self.onPrevBtn, 'Ctrl+P', 'Prev image')
        addAction(menu, self, '&Save', self.onSaveImg, 'Ctrl+S', 'Save image')

        layout1 = QVBoxLayout()

        self.gv = QGraphicsView()
        self.scene = QGraphicsScene()
        self.gv.setScene(self.scene)
        self.gv.installEventFilter(self)
        layout1.addWidget(self.gv)

        panel = QWidget(self)
        self.controlPanel = QHBoxLayout()
        panel.setLayout(self.controlPanel)
        layout1.addWidget(panel)

        center = QWidget()
        center.setLayout(layout1)
        self.setCentralWidget(center)

    def toggleHistogram(self):
        self.show_histogram = not self.show_histogram
        self.make_histogram()

    def eventFilter(self, obj, event):
        if obj == self.gv and event.type() == QEvent.MouseButtonPress:
            p = self.gv.mapToScene(event.pos())
            self.setLocation(p)
        return QWidget.eventFilter(self, obj, event)

    def setLocation(self, pos):
        if self.locator2 is not None:
            self.locator1 = None
            self.locator2 = None
        if self.locator1:
            self.locator2 = (pos.x(), pos.y())
            self.drawLocator()
        else:
            self.locator1 = (pos.x(), pos.y())

    def drawLocator(self):
        if self.locator:
            self.scene.removeItem(self.locator)
            self.locator = None
        pen = QPen(Qt.red, 3)
        self.locator = self.scene.addRect(self.locator1[0], self.locator1[1], self.locator2[0]-self.locator1[0], self.locator2[1]-self.locator1[1], pen)
        print('locator', self.locator1, self.locator2)
        self.gv.update() # self.label.update() #QApplication.processEvents()


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
            self.pilorig = PIL.Image.open(fileName)
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
        self.sizeImage()

    def sizeImage(self):
        orig = pil2pixmap(self.pilorig)
        if self.pilorig:
            if self.scaledPixmap:
                self.scene.removeItem(self.scaledPixmap)
                self.scaledPixmap = None
            if self.locator:
                self.scene.removeItem(self.locator)
                self.locator = None

            pixmap = orig.scaled(self.gv.width(), self.gv.height(),
                                      Qt.KeepAspectRatio,
                                      transformMode = Qt.SmoothTransformation)
            self.scaledPixmap = self.scene.addPixmap(pixmap)

            self.scale = (
                orig.size().width()/pixmap.size().width(),
                orig.size().height()/pixmap.size().height()
            )
            self.make_histogram()

    def absLocatorRect(self):
        return [
            self.locator1[0]*self.scale[0],
            self.locator1[1]*self.scale[1],
            self.locator2[0]*self.scale[0],
            self.locator2[1]*self.scale[1]
        ]

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
        fn = self.prevFileName()
        if fn:
            self.openImage(os.path.join(self.dirName, fn))

    def onSaveImg(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(
            self,
            "Save as ...",
            os.path.join(self.dirName, self.fileName),
            "All Files (*);;Jpeg Files(*.jpg)",
            options=options)
        if fileName:
            print(fileName)
            self.pilorig.save(fileName)

    def make_histogram(self): # should it be a ShowWin class method?
        #self.canvas.delete('histogram')
        for it in self.histogram:
            self.scene.removeItem(it)
        del self.histogram[:]
        if not self.show_histogram:
            return

        img = self.pilorig
        if not img:
            return
        h = img.convert("L").histogram()
        maxVal = 1
        for i in range(0, len(h)):
            if h[i] > maxVal:
                maxVal = h[i]
        _X = float(img.size[1])
        x = 100 if _X > 100 else _X

        penGray = QPen(Qt.gray, 3)
        penRed = QPen(Qt.red, 3)

        for i in range(0, len(h)):
            if h[i] == maxVal:
                pen = penRed
            else:
                pen = penGray
            self.histogram.append(self.scene.addLine(i, x, i, x - x * h[i] / maxVal, pen))

        self.histogram.append(self.scene.addRect(0, 0, len(h), x, penGray))
        self.gv.update()

    # support transformation plugins
    def controlImg(self, checkCtrl=True):
        if checkCtrl and not self.ctrl:
            return None
        else:
            return self.savedImg

    def setCtrl(self, ctrl):
        if ctrl and self.ctrl:
            return # do not allow two control panels
        if self.ctrl and not ctrl:
            self.ctrl.setParent(None)
        self.ctrl = ctrl
        if ctrl:
            self.controlPanel.addWidget(ctrl)
            self.savedImg = self.pilorig

    def unsetCtrl(self):
        if self.ctrl:
            self.ctrl.setParent(None)
            self.ctrl = None


if __name__ == '__main__':
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    appctxt.app.setStyle('Fusion')
    #appctxt.app.setStyleSheet("QPushButton { margin: 10ex; }")
    MyWindow().show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)