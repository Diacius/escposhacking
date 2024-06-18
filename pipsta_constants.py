from escpos.printer import Usb
from escpos import constants, codepages, exceptions
from bitarray import bitarray
ESC = b'\x1B'
'''
Initialise
'''
INITIALISE = ESC + b'\x40'


'''
Data is stored in buffer until FormFeed or GS,L to exit spooling
is recieved, or paper feed button is pressed
'''
ENTER_SPOOLING = b'\x1B\x4C'
'''
Exit Spooling
'''
EXIT_SPOOLING = constants.GS + b'L'
'''
Underline 1BH,2DH,n:
if n is 0 then underline is off; otherwise on
'''
UNDERLINE = b'\x1B\x2D' # Add n byte afterwards
'''
Print and feed extra paper, final byte is number of 1/20 lines to feed.
'''
PRINT_AND_FEED_EXTRA_PAPER = b'\x1B\x4A'
def printFeedExtra(lines:bytes):
    return PRINT_AND_FEED_EXTRA_PAPER + lines