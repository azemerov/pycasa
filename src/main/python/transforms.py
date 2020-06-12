import PIL.Image
#from PyCasa.simpledialog import EntriesDialog
import PIL.ImageEnhance
from PIL.ImageEnhance import Brightness
from PIL.ImageEnhance import Contrast
from PIL import ImageFilter, Image
from functools import reduce
#from PIL.ImageQt import ImageQt
#from PyQt5.QtGui import QPixmap
#from .main import pil2pixmap
from dialogs import BrightnessConstrastFrame, NumValFrame, OrtonFrame

editWindow = None
ctrl = None

def getImg(checkCtrl=True):
    global ctrl
    if checkCtrl and not ctrl:
        ctrl = None
        return None
    else:
        return editWindow.pilorig

def setCtrl(_ctrl=None):
    global ctrl
    if ctrl and not _ctrl:
        ctrl.setParent(None)
    ctrl = _ctrl
    if ctrl:
        editWindow.controlPanel.addWidget(ctrl)

###############################################

def _do_set_brightness(vals): #b, c):
    img = getImg()
    if img and vals and vals != (1,1):
        if vals[0] != 1:
            bright = Brightness(img)
            img = bright.enhance(vals[0])

        if vals[1] != 1:
            contr = Contrast(img)
            img = contr.enhance(vals[0])
        editWindow.updateImage(img) #win.update_img(img, True, label='set_brightness %f, %f'%(b, c), operation=do_set_brightness, params=(b,c))
    setCtrl(None)

def do_set_brightness():
    if ctrl: return
    setCtrl(BrightnessConstrastFrame(editWindow, 1.0, 1.0, _do_set_brightness))

###############################################

def _do_enh_contrast(c):
    img = getImg()
    if img and c and c!=1:
        enh = Contrast(img)
        img = enh.enhance(c)
        editWindow.updateImage(img) #win.update_img(img, True, label='enh_contrast %f'%c, operation=do_enh_contrast, params=(c,))
    setCtrl(None)

def do_enh_contrast():
    if ctrl: return
    setCtrl(NumValFrame(editWindow, 'Contrast:', 1.0, _do_enh_contrast))

###############################################

def _do_enh_sharpness(c):
    img = getImg()
    if img and c and c!=1:
        enh = PIL.ImageEnhance.Sharpness(img)
        img = enh.enhance(c)
        editWindow.updateImage(img) #win.update_img(img, True, label='enh_sharpness %f'%c, operation=do_enh_sharpness, params=(c,))
    setCtrl(None)

def do_enh_sharpness():
    if ctrl: return
    setCtrl(NumValFrame(editWindow, 'Sharpness:', 1.0, _do_enh_contrast))

###############################################

def do_equalize():
    img = getImg(False)
    if not img: return
    h = img.convert("L").histogram()
    import operator
    lut = []
    for b in range(0, len(h), 256):
        # step size
        step = reduce(operator.add, h[b:b+256]) / 255
        # create equalization lookup table
        n = 0
        for i in range(256):
            lut.append(n / step)
            n = n + h[i+b]
    # map image through lookup table
    try:
        layers = img.layers
    except AttributeError:
        if img.mode == "RGB":
            layers = 3
        elif img.mode == "RGBA":
            layers = 4
        else:
            raise Exception("don't know how many layers!")
    img = img.point(lut*layers)
    #from PIL.JpegImagePlugin import JpegImageFile
    #current_img = JpegImageFile(current_img)
    #qimg = ImageQt(img)
    editWindow.updateImage(img) #update_img(img, True, label='Equalize', operation=do_equalize, params=None)

###############################################

def do_transpose(method):
    img = getImg(False)
    if img:
        img = img.transpose(method)
        editWindow.updateImage(img) #update_img(img, True, label='Equalize', operation=do_equalize, params=None)

def _zoom(img, zoomFactor):
    if zoomFactor == 1:
        return img
    orig_size = img.size
    width, height = orig_size
    dx = int((width*zoomFactor - width)/2)
    dy = int((height*zoomFactor - height)/2)
    img = img.crop((dx, dy, width-dx, height-dy))
    img = img.resize((width, height), Image.NONE)
    return img

def _do_orthon(vals):
    global ctrl
    if not vals:
        ctrl = None
        return
    b1, b2, z, ba = vals
    img1 = getImg()
    if img1:
        img2 = img1
        enh = PIL.ImageEnhance.Brightness(img1)
        img1 = enh.enhance(b1)
        enh = PIL.ImageEnhance.Brightness(img2)
        img2 = enh.enhance(b2)
        img2 = _zoom(img2, z)
        img2 = img2.filter(ImageFilter.BLUR)
        img2 = img2.filter(ImageFilter.SMOOTH_MORE)

        img = Image.blend(img1, img2, ba)

        editWindow.updateImage(img) #win.update_img(img, True, label='orthon %f %f %f %f'%(b1, b2, z, ba), operation=do_orthon, params=(b1, b2, z, ba))
    setCtrl(None)

def do_orthon():
    if ctrl: return
    setCtrl(OrtonFrame(editWindow, 1.1, 1.3, 1.01, 0.3, _do_orthon))

def getTransforms():
    return [
        ('Se&t Brightness/Contrast', None,do_set_brightness, 'Ctrl+T', None),
        ('Set &Contrast',   None, do_enh_contrast, 'Ctrl+Shift+C', None),
        ('Enchance &Sharpness',None, do_enh_sharpness, 'Ctrl+Shift+S', None),
        ('&Equalize',       None, do_equalize, None, None),
        ('Rotait &left',    None, lambda: do_transpose(Image.ROTATE_90), None, None),
        ('&Rotait right',   None, lambda: do_transpose(Image.ROTATE_270), None, None),
        ('Flip &horizontal',None, lambda: do_transpose(Image.FLIP_LEFT_RIGHT), None, None),
        ('Flip &vertical',  None, lambda: do_transpose(Image.FLIP_TOP_BOTTOM), None, None),
        ('&Orthon',         None, lambda: do_orthon(), 'Ctrl+Alt+O', None)
]
