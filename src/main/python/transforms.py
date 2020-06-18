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

###############################################

def _do_set_brightness(vals): #b, c):
    img = editWindow.controlImg()
    if not vals: # rollback
        editWindow.updateImage(editWindow.savedImg)
    if img and vals and vals != (1,1):
        if vals[0] != 1:
            bright = Brightness(img)
            img = bright.enhance(vals[0])

        if vals[1] != 1:
            contr = Contrast(img)
            img = contr.enhance(vals[0])
        editWindow.updateImage(img) #win.update_img(img, True, label='set_brightness %f, %f'%(b, c), operation=do_set_brightness, params=(b,c))
    editWindow.unsetCtrl()

def _onBrightnessChange(value):
    img = editWindow.controlImg(False)
    try:
        val = float(value)
        bright = Brightness(img)
        img = bright.enhance(val)
        editWindow.updateImage(img)
    except:
        pass

def _onContrastChange(value):
    img = editWindow.controlImg(False)
    try:
        val = float(value)
        contr = Contrast(img)
        img = contr.enhance(val)
        editWindow.updateImage(img)
    except:
        pass

def do_set_brightness():
    editWindow.setCtrl(BrightnessConstrastFrame(editWindow, 1.0, 1.0, _do_set_brightness, _onBrightnessChange, _onContrastChange))

###############################################

def _do_enh_contrast(c):
    img = editWindow.controlImg()
    if img and c and c!=1:
        enh = Contrast(img)
        img = enh.enhance(c)
        editWindow.updateImage(img) #win.update_img(img, True, label='enh_contrast %f'%c, operation=do_enh_contrast, params=(c,))
    editWindow.unsetCtrl()

def do_enh_contrast():
    editWindow.setCtrl(NumValFrame(editWindow, 'Contrast:', 1.0, _do_enh_contrast))

###############################################

def _do_enh_sharpness(c):
    img = editWindow.controlImg()
    if img and c and c!=1:
        enh = PIL.ImageEnhance.Sharpness(img)
        img = enh.enhance(c)
        editWindow.updateImage(img) #win.update_img(img, True, label='enh_sharpness %f'%c, operation=do_enh_sharpness, params=(c,))
    editWindow.unsetCtrl()

def do_enh_sharpness():
    editWindow.setCtrl(NumValFrame(editWindow, 'Sharpness:', 1.0, _do_enh_contrast))

###############################################

def _do_enh_color(c=None):
    img = editWindow.controlImg()
    if not img or c==1: return
    enh = PIL.ImageEnhance.Color(img)
    img = enh.enhance(c)
    editWindow.updateImage(img) #win.update_img(img, True, label='enh_color %f'%c, operation=do_enh_color, params=(c,))
    editWindow.unsetCtrl()

def do_enh_color():
    editWindow.setCtrl(NumValFrame(editWindow, 'Color:', 1.2, _do_enh_color))

###############################################

def do_crop():
    # todo: apply scale factor between pilorig and orig
    img = editWindow.controlImg(False)
    if not img:
        return
    if editWindow.locator2 is None:
        return
    img = img.crop(editWindow.absLocatorRect())
    editWindow.updateImage(img) #win.update_img(img, True, label='crop %s'%locator, operation=do_crop, params=(locator,))
    #todo: editWindow.canvas.delete('locators')
    #todo: editWindow.locator = [None,None,None,None]


###############################################

def do_equalize():
    img = editWindow.controlImg(False)
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
    img = editWindow.controlImg(False)
    if img:
        img = img.transpose(method)
        editWindow.updateImage(img) #update_img(img, True, label='Equalize', operation=do_equalize, params=None)

###############################################

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

def _do_zoom(value, checkCtrl=False):
    img = editWindow.controlImg(checkCtrl)
    if not img or float(value)==1:
        return
    img = _zoom(img, float(value))
    editWindow.updateImage(img) #win.update_img(img, True, label='zoom %f'%z, operation=do_zoom, params=(z,))
    editWindow.unsetCtrl()

def do_zoom(value=None):
    if value:
        _do_zoom(value, False)
    else:
        editWindow.setCtrl(NumValFrame(editWindow, 'Zoom factor:', 2.0, _do_zoom))

###############################################

def _do_resize(value, checkCtrl=True):
    img = editWindow.controlImg(checkCtrl)
    f = float(value)
    if not img or f==1:
        return
    orig_size = img.size
    width, height = orig_size
    img = img.resize((int(width*f), int(height*f)), Image.ANTIALIAS)
    editWindow.updateImage(img) #win.update_img(img, True, label='resize %f'%f, operation=do_resize, params=(f,))
    editWindow.unsetCtrl()

def do_resize(value=None):
    if value:
        _do_resize(value, False)
    else:
        editWindow.setCtrl(NumValFrame(editWindow, 'Resize factor:', 2.0, _do_resize))

###############################################

def _do_orthon(vals):
    if vals:
        b1, b2, z, ba = vals
        img1 = editWindow.controlImg()
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
    editWindow.unsetCtrl()

def do_orthon():
    editWindow.setCtrl(OrtonFrame(editWindow, 1.1, 1.3, 1.01, 0.3, _do_orthon))

###############################################

def do_blend():
    img1 = editWindow.controlImg()
    if not img1: return
    img2 = editWindow.saved
    if not img2: return
    #if not c:
    c = 0.5
    img = Image.blend(img1, img2, c)
    editWindow.updateImage(img) #win.update_img(img, True, label='blend %f'%c, operation=so_blend, params=(c,))

###############################################

def do_filter(imgFilter):
    img = editWindow.controlImg(False)
    if not img: return
    img = img.filter(imgFilter)
    editWindow.updateImage(img) #win.update_img(img, True, label='filter %s'%filter, operation=do_filter, params=(filter,))

###############################################

def getTransforms():
    return [
        ('Brigh&tness',     None, do_set_brightness,    'Ctrl+T', None),
        ('Set &Contrast',   None, do_enh_contrast,      'Ctrl+Shift+C', None),
        ('&Sharpness',      None, do_enh_sharpness,     'Ctrl+Shift+S', None),
        ('Co&lor',          None, do_enh_color,         None, None),
        ('&Equalize',       None, do_equalize,          None, None),
        ('Rotait &left',    None, lambda: do_transpose(Image.ROTATE_90),        None, None),
        ('&Rotait right',   None, lambda: do_transpose(Image.ROTATE_270),       None, None),
        ('Flip &horizontal',None, lambda: do_transpose(Image.FLIP_LEFT_RIGHT),  None, None),
        ('Flip &vertical',  None, lambda: do_transpose(Image.FLIP_TOP_BOTTOM),  None, None),

        ('&Orthon',         None, do_orthon,            'Ctrl+Alt+O', None),
        ('&Blend',          None, lambda: do_blend(),   'Ctrl+Alt+B', None),

        ('&Blur',           None, lambda: do_filter(ImageFilter.BLUR),          'Ctrl+X|Ctrl+B', None),
        ('&Contour',        None, lambda: do_filter(ImageFilter.CONTOUR),       'Ctrl+X|Ctrl+C', None),
        ('&Detail',         None, lambda: do_filter(ImageFilter.DETAIL),        'Ctrl+X|Ctrl+D', None),
        ('&Edge',           None, lambda: do_filter(ImageFilter.EDGE_ENHANCE),  'Ctrl+X|Ctrl+E', None),
        ('&Edge more',      None, lambda: do_filter(ImageFilter.EDGE_ENHANCE_MORE), None, None),
        ('Emb&oss',         None, lambda: do_filter(ImageFilter.EMBOSS),        'Ctrl+X|Ctrl+G', None),
        ('&Find edges',     None, lambda: do_filter(ImageFilter.FIND_EDGES),    'Ctrl+X|Ctrl+S', None),
        ('&Sharpen',        None, lambda: do_filter(ImageFilter.SHARPEN),       'Ctrl+X|Ctrl+H', None),
        ('&Smooth',         None, lambda: do_filter(ImageFilter.SMOOTH),        None, None),
        ('&Smooth more',    None, lambda: do_filter(ImageFilter.SMOOTH_MORE),   None, None),

        ('&Crop',           None, lambda: do_crop(),        None, None),
        ('&Zoom',           None, lambda: do_zoom(None),    'Ctrl+Shift+Z', None),
        ('Zoom &In',        None, lambda: do_zoom(1.2),     'Alt+I', None),
        ('Zoom &Out',       None, lambda: do_zoom(0.8),     'Alt+O', None),
        ('Resize &In',      None, lambda: do_resize(2.0),   'Alt+Shift+I', None),
        ('Resize &Out',     None, lambda: do_resize(0.5),   'Alt+Shift+O', None),
]

