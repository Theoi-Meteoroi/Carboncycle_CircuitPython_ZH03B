# The MIT License (MIT)
#
# Copyright (c) 2020 Dave Thompson for CarbonCycle
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`carboncycle_zh03b`
================================================================================

CircuitPython library for the Winsen ZH03B laser particle sensor, directly connected to a serial port.  Allows fan  control and power reduction by controlling sensor mode. CircuitPython 5.0 and later.


* Author(s): Dave Thompson

Implementation Notes
--------------------

**Hardware:**

.. todo:: Add links to any specific hardware product page(s), or category page(s). Use unordered list & hyperlink rST
   inline format: "* `Link Text <url>`_"

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

.. todo:: Uncomment or remove the Bus Device and/or the Register library dependencies based on the library's use of either.

# * Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
# * Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""

# imports

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/Theoi-Meteoroi/Carboncycle_CircuitPython_ZH03B.git"

#   v0.1  ZH03B.py module for CircuitPython
#   3/26/2020  Dave Thompson
#
#   ZH03B 
#
#   Caller needs to keep track of sleep, Q&A modes in use. No state stored.
#   Modify PORT setting below for your specific device entry.
#
#
import board
import busio
import digitalio
from adafruit_binascii import hexlify

uart = busio.UART(board.TX, board.RX, baudrate=9600)

uart.reset_input_buffer() #flush input buffer

def SetQA():
    """
    Set ZH03B Question and Answer mode
    Returns:  Nothing
    """
    uart.write( b"\xFF\x01\x78\x41\x00\x00\x00\x00\x46")
    return

def SetStream():
    """
    Set to default streaming mode of readings
    Returns: Nothing
    """
    uart.write( b"\xFF\x01\x78\x40\x00\x00\x00\x00\x47")
    return

def QAReadSample():
    """
    Q&A mode requires a command to obtain a reading sample
    Returns: int PM1, int PM25, int PM10
    """
    uart.reset_input_buffer()
    uart.write( b"\xFF\x01\x86\x00\x00\x00\x00\x00\x79")
    reading = ((hexlify(uart.read(2))),16)
    PM25 = int((hexlify(uart.read(2))),16)
    PM10 = int((hexlify(uart.read(2))),16)
    PM1 = int((hexlify(uart.read(2))),16)
    return( PM1, PM25, PM10 )

########

def DormantMode(pwr_status):
    """
    Turn dormant mode on or off. Must be on to measure.
    """
    #  Turn fan off
    #
    if pwr_status == "sleep":
       uart.reset_input_buffer()
       uart.write( b"\xFF\x01\xA7\x01\x00\x00\x00\x00\x57")
       response = (hexlify(uart.read(7)))
       response = (hexlify(uart.read(3)))
       if response == b'ffa701':
          uart.reset_input_buffer()
          return ("FanOFF")
       else:
          uart.reset_input_buffer()
          return ("FanERROR")


    #  Turn fan on
    #
    if pwr_status == "run":
       uart.reset_input_buffer() 
       uart.write( b"\xFF\x01\xA7\x00\x00\x00\x00\x00\x58")
       #response = (hexlify(uart.read(14)))
       response = (hexlify(uart.read(3)))
       if response == b'ffa701':
          uart.reset_input_buffer()
          return ("FanON")
       else:
          uart.reset_input_buffer()
          return ("FanERROR")


########

def ReadSample():
    """
    Read exactly one sample from the default mode streaming samples
    """
    uart.reset_input_buffer()
    sampled = False
    while not sampled:
      reading = uart.read(2)
      if reading == b'BM':
          sampled = True
          status = uart.read(8)
          PM1 = int((hexlify(uart.read(2))),16)
          PM25 = int((hexlify(uart.read(2))),16)
          PM10 = int((hexlify(uart.read(2))),16)
          return ( PM1, PM25, PM10 )
      else:
        continue

