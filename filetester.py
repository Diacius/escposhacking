import escpos.printer as printer, escpos.exceptions, escpos.escpos
import pipsta_constants
a = printer.File('output.bin')
a.image('testimg.bmp', impl="bitImageColumn")