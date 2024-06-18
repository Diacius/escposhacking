# Constants
USB_vendor = 0x0483
USB_product = 0xa19d
# Newlines to get print above the tear bar - you may want to change this for your printer
feed_to_bar = '\n\n\n\n'
from escpos.printer import Usb
from escpos import constants, codepages, exceptions
import pipsta_constants
# Setup a temporary connection to check we can connect to the printer
try:
    usb = Usb(USB_vendor, USB_product, 0, out_ep=0x2)
    usb.close()
except exceptions.DeviceNotFoundError:
    print("Printer failed to be found")
# Setup connection to printer
usb = Usb(USB_vendor, USB_product, 0, out_ep=0x2)
# print test graphics data
usb._raw(pipsta_constants.UNDERLINE + b'\x01Testing' + pipsta_constants.PRINT_AND_FEED + b'\x28')


usb.close()
