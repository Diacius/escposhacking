USB_vendor = 0x0483
USB_product = 0xa19d
# Newlines to get print above the tear bar - you may want to change this for your printer
feed_to_bar = '\n\n\n\n'

from escpos.printer import Usb
# Setup a temporary connection to check we can connect to the printer
usb = Usb(USB_vendor, USB_product, 0, out_ep=0x2)
usb.close()
# Setup connection to printer
usb = Usb(USB_vendor, USB_product, 0, out_ep=0x2)
# dummy data for testing
post_data = "fejheguio"
print(post_data)
# Print out the recieved message,e
#usb.text(post_data + '\n')
# CUSTOM CODE PRODUCE TEST PRINT
usb._raw('\x1B\x2D@@@\x1B\x4A\x04')


usb.close()
