# TODO: Add pipsta image support
import escpos.printer as printer, escpos.exceptions, escpos.escpos
import pipsta_constants as constants
from escpos.image import EscposImage
import math
from typing import Iterator, Union
from PIL import Image, ImageOps, ImageFilter
import struct
import bitarray
import os
from time import sleep
USB_vendor = 0x0483
USB_product = 0xa19d
ESC = constants.ESC
SET_FONT_MODE_3 = b'\x1b!\x00'
SET_LED_MODE = b'\x1bX\x2d'
FEED_PAST_CUTTER = b'\n' * 5
SELECT_SDL_GRAPHICS = b'\x1b*\x08'
USB_BUSY = 66
def convert_image(image):
    #imagebits = bitarray.bitarray(image.getdata(), endian='big')
    #imagebits.invert()
    return image.getdata()
def load_image(filename):
    '''Loads an image from the named png file.  Note that the extension must
    be omitted from the parameter.
    '''
    return Image.open(filename).convert('1')
def print_image(ep_out, data):
    '''Reads the data and sends it a dot line at once to the printer
    '''
    try:
        ep_out._raw(SET_FONT_MODE_3)
        cmd = struct.pack('3s2B', SELECT_SDL_GRAPHICS,(DOTS_PER_LINE / 8) & 0xFF,(DOTS_PER_LINE / 8) / 256)
        # Arbitrary command length, set to minimum acceptable 24x8 dots this figure
        # should give mm of print
        lines = len(data)//BYTES_PER_DOT_LINE
        start = 0
        for line in range (0, lines):    
            start = line * BYTES_PER_DOT_LINE
            # intentionally +1 for slice operation below
            end = start + BYTES_PER_DOT_LINE
            # ...to end (end not included)            
            ep_out._raw(b''.join([cmd, data[start:end]]))
    finally:
        #ep_out.write(RESTORE_DARKNESS)
        pass
def main():        
    '''This is the main loop where arguments are parsed, connections
     are established, images are processed and the result is
    printed out.
    '''
    usb = printer.Usb(USB_vendor, USB_product, 0, out_ep=0x2)
    # Print it out
    try:
        im = Image.open('ghastly.png') # Open colour image
        im = im.resize(size=(384,im.height),resample=Image.Resampling.LANCZOS)
        im = im.convert("1")
        print(list(im.getdata()))
        im.save('test.bmp')
        usb.hw('INIT')
        usb._raw(SET_FONT_MODE_3)
        usb._raw(constants.ENTER_SPOOLING)
        # From http://stackoverflow.com/questions/273946/
        #/how-do-i-resize-an-image-using-pil-and-maintain-its-aspect-ratio
        DOTS_PER_LINE = 384
        BYTES_PER_DOT_LINE = 48 #(48)
        # ESC, *, 8(for dots), n1,n2,
        # first bit most signif
        # The number of dot columns is given by (n1+ 256*n2)
        for i in range(8192):
            usb._raw(ESC+b'*\x08\x40\x01' + b'\x0E'*24)
            usb._raw(ESC+b'*\x08\x40\x01' + b'\x02'*24)
        usb._raw(constants.EXIT_SPOOLING)
        usb.text('\n\n\n\n')
    finally:
        # Ensure the LED is not in test mode
        usb._raw(SET_LED_MODE + b'\x00')
        
if __name__ == '__main__':
    main()

header = (ESC + b"*" + b"\x08")
