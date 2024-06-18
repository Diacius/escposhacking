# Constants
USB_vendor = 0x0483
USB_product = 0xa19d
# Newlines to get print above the tear bar - you may want to change this for your printer
feed_to_bar = '\n\n\n\n'
import escpos.printer as printer, escpos.exceptions, escpos.escpos
import pipsta_constants
# Setup a temporary connection to check we can connect to the printer
try:
    usb = printer.Usb(USB_vendor, USB_product, 0, out_ep=0x2)
    usb.close()
except escpos.exceptions.DeviceNotFoundError:
    print("Printer failed to be found")
# Setup connection to printer
usb = printer.Usb(USB_vendor, USB_product, 0, out_ep=0x2)
# Reset formatting
usb.hw('INIT')
# Test spooling
usb._raw(pipsta_constants.ENTER_SPOOLING)
usb.text('Testing\n')
usb.text('£€\n') # € prints as ñ, TODO: Add custom codepage so it's corrrect
# Images currently borked
#usb.image(img_source='testimg.bmp',impl='bitImageColumn',center=True)
# 0x32 is DEC: 50 or 2.5 lines (1 line is 20/0x14)
usb._raw(pipsta_constants.printFeedExtra(b'\x32'))
# Exit spooling, which should print the full output.
usb._raw(pipsta_constants.EXIT_SPOOLING)