# Change these to the correct values for your device
# You can find the values on linux using `lsusb`
USB_vendor = 0x0483
USB_product = 0xa19d
# Newlines to get print above the tear bar - you may want to change this for your printer
feed_to_bar = '\n\n\n\n'

from escpos.printer import Usb
# Setup a temporary connection to check we can connect to the printer
usb = Usb(USB_vendor, USB_product, 0, out_ep=0x2)
usb.close()

from flask import Flask, request, Response
import json
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def respond():
    # Setup connection to printer
    usb = Usb(USB_vendor, USB_product, 0, out_ep=0x2)
    # Get the JSON data from the request and print the recieved message *to the screen*
    post_data = request.json
    print(post_data["msg"])
    # Print out the recieved message, close the connection, and return a simple HTTP OK response
    usb.text(post_data["msg"] + feed_to_bar)
    usb.close()
    return Response("PRINTED", status=200)
