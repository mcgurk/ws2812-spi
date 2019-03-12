#!/usr/bin/python
NumpyImported=False
try:
    import numpy
    from numpy import sin, cos, pi
    NumpyImported=True
except ImportError:
    #print("Warning: no numpy found, routines will be slow")
    pass
"""
T0H: 0.35   -> 2p=0.31  3p=0.47
T0L: 0.80   -> 6p=0.94  5p=0.78
T1H: 0.70   -> 4p=0.625 5p=0.78
T1L: 0.60   -> 4p=0.625 3p=0.47
"""

def write2812_numpy4(spi, data):
    d=numpy.array(data).ravel()
    tx=numpy.zeros(len(d)*4, dtype=numpy.uint8)
    for ibit in range(4):
        tx[3-ibit::4]=((d>>(2*ibit+1))&1)*0x60 + ((d>>(2*ibit+0))&1)*0x06 +  0x88
    spi.max_speed_hz = int(4/1.05e-6)
    spi.writebytes(tx.tolist())

def write2812_pylist4(spi, data):
    tx=[]
    for rgb in data:
        for byte in rgb:
            for ibit in range(3,-1,-1):
                tx.append(((byte>>(2*ibit+1))&1)*0x60 +
                          ((byte>>(2*ibit+0))&1)*0x06 +
                          0x88)
    spi.max_speed_hz = int(4/1.05e-6)
    spi.writebytes(tx)

if NumpyImported:
    write2812=write2812_numpy4
else:
    write2812=write2812_pylist4

if __name__=="__main__":
    import spidev
    import time
    import getopt
    import sys

    def test_fixed(spi):
        #write fixed pattern for 8 LEDs
        #This will send the following colors:
        #   Red, Green, Blue,
        #   Purple, Cyan, Yellow,
        #   Black(off), White
        write2812(spi, [[10,0,0], [0,10,0], [0,0,10],
                        [0,10,10], [10,0,10], [10,10,0],
                        [0,0,0], [10,10,10]])
    def test_off(spi, nLED=8):
        #switch all nLED chips OFF.
        write2812(spi, [[0,0,0]]*nLED)


    try:
        opts, args = getopt.getopt(sys.argv[1:], "hn:c:t", ["help", "color=", "test"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err)) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    color=None
    nLED=8
    doTest=False
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-c", "--color"):
            color=a
        elif o in ("-n", "--nLED"):
            nLED=int(a)
        elif o in ("-t", "--test"):
            doTest=True
            assert False, "unhandled option"

    spi = spidev.SpiDev()
    spi.open(0,0)

    if color!=None:
        write2812(spi, eval(color)*nLED)
    elif doTest:
        test_fixed(spi, nLED)
    else:
        usage()


