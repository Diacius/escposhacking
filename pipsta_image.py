# TODO: Add pipsta image support
import escpos.printer as printer, escpos.escpos
from pipsta_constants import ENTER_SPOOLING, EXIT_SPOOLING, ESC
from PIL import Image
from bitarray import bitarray
from time import sleep
USB_vendor = 0x0483
USB_product = 0xa19d
SET_FONT_MODE_3 = b'\x1b!\x00'
SET_LED_MODE = b'\x1bX\x2d'
FEED_PAST_CUTTER = b'\n' * 5
SELECT_SDL_GRAPHICS = b'\x1b*\x08'
USB_BUSY = 66
def printImg(usbvendor, usbproduct, filename):        
    '''
    Convert the image to 1bit black and white, and then create a bitarray of the
    1 bit data, then print it out in 48byte chunks @ 48B/line for 384 pixels of horizontal resolution!
    '''
    # Create printer connectiom
    usb = printer.Usb(usbvendor, usbproduct, 0, out_ep=0x2)
    im = Image.open(filename) # Open the colour image
    im = im.convert("1") # Make 1-bit monochrome
    im = im.resize(size=(384,im.height),resample=Image.Resampling.NEAREST) # Resize the image so that it is the correct width!
    pixellist = list(im.getdata()) # Generate a list containing every pixel as either 255 or 0.
    usb.hw('INIT') # Ensure that the printer is initialised, in case underline or other formatting is left on.
    usb._raw(SET_FONT_MODE_3) # Set the font to 3, TODO: Is this needed? If so, why?
    DOTS_PER_LINE = 384
    BYTES_PER_DOT_LINE = DOTS_PER_LINE//8 #(48)
    # ESC, *, 8(for dots), n1,n2,
    # first bit most significant, printed with first bit top-left
    # The number of bytes is given by (n1+ 256*n2)
    # Therefore we make  n1 for 48 bytes and n2 0
    DOTHEADER = ESC+b'*\x08\x30\x00'
    # Create a big endian bitarray, because the first bit gets printed first
    pixelarray1bit = bitarray(endian='big')
    # TODO: This is a little messy, can this be improved?
    for i in pixellist:
        # If the pixel is white it's a 0 for no dot
        if i == 255:
            pixelarray1bit.append(0)
        # If the pixel is black it's a 1 for a dot
        if i == 0:
            pixelarray1bit.append(1)
    # Convert the continous bitarray to bytes
    imgbytes = pixelarray1bit.tobytes()
    # Find the number of lines by dividing the number of bytes by the bytes per line value
    number_of_lines = len(imgbytes) // BYTES_PER_DOT_LINE
    # Tell the printer to start spooling, so that processing does not cause the image to have gaps
    usb._raw(ENTER_SPOOLING)
    # For each line
    for i in range(number_of_lines):
        # Build the data to send to the printer from:
        # The header for dot-by-dot line printing
        # The image's bytes from: line number * bytes_per_line to that plus the bytes per line to get the data
        # in chunks for each line (usually 48 bytes)
        construct = DOTHEADER + imgbytes[i*BYTES_PER_DOT_LINE:(BYTES_PER_DOT_LINE*i)+BYTES_PER_DOT_LINE]
        # Send the built data to the printer as raw bytes using escpos' IO tools
        usb._raw(construct)
        # TODO: A hardcoded sleep isn't paticularly sensible, the library supports reading the output
        # So lets work out how to wait until the data is processed correctly :)
        sleep(0.01)
    # Feed to the tear bar :)
    usb.text('\n\n\n\n')
    # Exit spooling mode which will print the buffer
    usb._raw(EXIT_SPOOLING)
    usb.close()
# Demo with the testimage if the file is run individually :)        
if __name__ == '__main__':
    printImg(usbproduct=USB_product, usbvendor=USB_vendor, filename='testimg.png')
