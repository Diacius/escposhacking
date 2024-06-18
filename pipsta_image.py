# TODO: Add pipsta image support
import escpos.printer as printer, escpos.exceptions, escpos.escpos
import pipsta_constants as constants
from escpos.image import EscposImage
import math
from typing import Iterator, Union
from PIL import Image, ImageOps, ImageFilter
import struct
from bitarray import bitarray
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
        print(im.width)
        print(im.height)
        pixellist = list(im.getdata())
        im.save('test.bmp')
        usb.hw('INIT')
        usb._raw(SET_FONT_MODE_3)
        # From http://stackoverflow.com/questions/273946/
        #/how-do-i-resize-an-image-using-pil-and-maintain-its-aspect-ratio
        DOTS_PER_LINE = 384
        BYTES_PER_DOT_LINE = DOTS_PER_LINE//8 #(48)
        # ESC, *, 8(for dots), n1,n2,
        # first bit most signif
        # The number of dot columns is given by (n1+ 256*n2)
        DOTHEADER = ESC+b'*\x08\x80\x01'
        pixelarray1bit = bitarray(endian='big')
        for i in pixellist:
            if i == 255:
                pixelarray1bit.append(1)
            if i == 0:
                pixelarray1bit.append(0)
        imgbytes = pixelarray1bit.tobytes()
        with open('testoutput.bin', 'wb') as handle:
            handle.write(imgbytes)
        # Find the number of lines by dividing the number of bytes by the bytes per line value
        number_of_lines = len(imgbytes) // BYTES_PER_DOT_LINE
        with open('testoutput.bin', 'wb') as handle:
            for i in range(number_of_lines):
                # TODO: maybe split somehow here?!?!?!
                handle.write((b'\x1B\x2A\x08\x80\x01' + imgbytes[i:BYTES_PER_DOT_LINE+i]))
            handle.close()
        usb.text('\n\n\n\n')
    finally:
        # Ensure the LED is not in test mode
        pass
        
if __name__ == '__main__':
    main()

header = (ESC + b"*" + b"\x08")
