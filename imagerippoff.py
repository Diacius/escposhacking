# image_print.py
# $Rev$
# Copyright (c) 2014 Able Systems Limited. All rights reserved.
'''This simple code example is provided as-is, and is for demonstration
purposes only. Able Systems takes no responsibility for any system
implementations based on this code.

This is an example of how a script can be written that uses a python graphics
library (in this case Pillow - see http://pillow.readthedocs.org/index.html)
to:
    load an image file,
    scale it to fit the page,
    Save and reopen (with dither) 
    and finally print the image using single dot graphics.

Note that dithering must happen AFTER the resizing to avoid a resize on the
dithered pixels giving rise to an inconsistent/mottled patter

Also note that the results of dithering are not always acceptable: 
please ensure all images in use convert acceptably for your application!

The files accompanying this script are:
    image.png - an example of a manually pre-processed dither
    scratch_logo.png - A predominantly yellow image that converts well
    programetc.png - a multicolour image betraying the limits of the dither

Copyright (c) 2015, Able Systems Ltd. All rights reserved.
'''

import argparse
import logging
import platform
import struct
import os
import sys
import time
import inspect

from bitarray import bitarray
import usb.core
import usb.util

from PIL import Image, ImageDraw


#import struct
MAX_PRINTER_DOTS_PER_LINE = 384
LOGGER = logging.getLogger('image_print.py')

# USB specific constant definitions
PIPSTA_USB_VENDOR_ID = 0x0483
PIPSTA_USB_PRODUCT_ID = 0xA19D
AP1400_USB_PRODUCT_ID = 0xA053
AP1400V_USB_PRODUCT_ID = 0xA19C

valid_usb_ids = {PIPSTA_USB_PRODUCT_ID, AP1400_USB_PRODUCT_ID, AP1400V_USB_PRODUCT_ID}

class printer_finder(object):
    def __call__(self, device):
        if device.idVendor != PIPSTA_USB_VENDOR_ID:
            return False

        return True if device.idProduct in valid_usb_ids else False

# Printer commands
SET_FONT_MODE_3 = b'\x1b!\x03'
SET_LED_MODE = b'\x1bX\x2d'
FEED_PAST_CUTTER = b'\n' * 5
SELECT_SDL_GRAPHICS = b'\x1b*\x08'


DOTS_PER_LINE = 384
BYTES_PER_DOT_LINE = DOTS_PER_LINE/8
USB_BUSY = 66


def setup_logging():
    '''Sets up logging for the application.'''
    LOGGER.setLevel(logging.INFO)

    file_handler = logging.FileHandler('mylog.txt')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(message)s',
                                                datefmt='%d/%m/%Y %H:%M:%S'))

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    LOGGER.addHandler(file_handler)
    LOGGER.addHandler(stream_handler)


def setup_usb():
    '''Connects to the 1st Pipsta found on the USB bus'''
    # Find the Pipsta's specific Vendor ID and Product ID (also known as vid
    # and pid)
    dev = usb.core.find(custom_match=printer_finder())
    if dev is None:                 # if no such device is connected...
        raise IOError('Printer not found')  # ...report error

    try:
        dev.reset()

        # Initialisation. Passing no arguments sets the configuration to the
        # currently active configuration.
        dev.set_configuration()
    except usb.core.USBError as err:
        raise IOError('Failed to configure the printer', err)

    # Get a handle to the active interface
    cfg = dev.get_active_configuration()

    interface_number = cfg[(0, 0)].bInterfaceNumber
    usb.util.claim_interface(dev, interface_number)
    alternate_setting = usb.control.get_interface(dev, interface_number)
    intf = usb.util.find_descriptor(
        cfg, bInterfaceNumber=interface_number,
        bAlternateSetting=alternate_setting)

    ep_out = usb.util.find_descriptor(
        intf,
        custom_match=lambda e:
        usb.util.endpoint_direction(e.bEndpointAddress) ==
        usb.util.ENDPOINT_OUT
    )

    if ep_out is None:  # check we have a real endpoint handle
        raise IOError('Could not find an endpoint to print to')
    
    return ep_out, dev


def convert_image(image):
    '''Takes the bitmap and converts it to PIPSTA 24-bit image format'''
    imagebits = bitarray(image.getdata(), endian='big')
    LOGGER.info("Done decoding!")
    # pylint: disable=E1101
    imagebits.invert()
    return imagebits.tobytes()


def print_image(device, ep_out, data):
    '''Reads the data and sends it a dot line at once to the printer
    '''
    LOGGER.debug('Start print')
    try:
        ep_out.write(SET_FONT_MODE_3)
        cmd = struct.pack('3s2B', SELECT_SDL_GRAPHICS,
                      (DOTS_PER_LINE / 8) & 0xFF,
                      (DOTS_PER_LINE / 8) / 256)
        # Arbitrary command length, set to minimum acceptable 24x8 dots this figure
        # should give mm of print
        lines = len(data)//BYTES_PER_DOT_LINE
        start = 0
        for line in range (0, lines):    
            start = line * BYTES_PER_DOT_LINE
            # intentionally +1 for slice operation below
            end = start + BYTES_PER_DOT_LINE
            # ...to end (end not included)            
            ep_out.write(b''.join([cmd, data[start:end]]))
        
        res = device.ctrl_transfer(0xC0, 0x0E, 0x020E, 0, 2)
        while res[0] == USB_BUSY:
                time.sleep(0.01)
                res = device.ctrl_transfer(0xC0, 0x0E, 0x020E, 0, 2)
                LOGGER.debug('End print')
    finally:
        #ep_out.write(RESTORE_DARKNESS)
        pass

def parse_arguments():
    '''Parse the filename argument passed to the script. If no
    argument is supplied, a default filename is provided.
    '''
    default_file = "image.png"
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='the image file to print',
                        nargs='?', default=default_file)
    return parser.parse_args()

def load_image(filename):
    '''Loads an image from the named png file.  Note that the extension must
    be omitted from the parameter.
    '''
    if not os.path.isfile(filename):
        root_dir = os.path.dirname(os.path.abspath(inspect.stack()[-1][1]))
        filename = os.path.join(root_dir, filename)
        
    return Image.open(filename).convert('1')

def main():        
    '''This is the main loop where arguments are parsed, connections
     are established, images are processed and the result is
    printed out.
    '''

    # This script is written using the PIL which requires Python 2
    #if sys.version_info[0] != 2:
    #    sys.exit('This application requires python 2.')

    if platform.system() != 'Linux':
        sys.exit('This script has only been written for Linux')
    
    args = parse_arguments()
    setup_logging()
    usb_out, device = setup_usb()
    usb_out.write(SET_LED_MODE + b'\x01')

    # Print it out
    try:
        im = Image.open(args.filename) # Open colour image
     
        # From http://stackoverflow.com/questions/273946/
        #/how-do-i-resize-an-image-using-pil-and-maintain-its-aspect-ratio
        wpercent = (DOTS_PER_LINE/float(im.size[0]))
        hsize = int((float(im.size[1])*float(wpercent)))
        im = im.resize((DOTS_PER_LINE,hsize), Image.ANTIALIAS)
        im.save("temp.png") # Save temporary colour image
        
        im = load_image("temp.png") # Reopen image (with dither)
        
        print_data = convert_image(im)
        usb_out.write(SET_LED_MODE + b'\x00')
        print_image(device, usb_out, print_data)
        usb_out.write(FEED_PAST_CUTTER)
    finally:
        # Ensure the LED is not in test mode
        usb_out.write(SET_LED_MODE + b'\x00')
        
if __name__ == '__main__':
    main()
