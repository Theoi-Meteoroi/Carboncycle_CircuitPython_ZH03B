import time
import board
import busio
from adafruit_binascii import hexlify

uart = busio.UART(board.TX, board.RX, baudrate=9600)
uart.reset_input_buffer()   # flush input buffer

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

test_status = 'run'

PM1, PM25, PM10 = ReadSample()
print("ReadSample output - First iteration")
print(PM1)
print(PM25)
print(PM10)
time.sleep(.5)

loopcount = 0

while test_status is not "ERROR":

    print("LoopCount=", loopcount)
    SetQA()
    print("QA set")
    time.sleep(.05)
    PM1, PM25, PM10 = QAReadSample()
    print("QA readsample", PM1, PM25, PM10)
    print(" Set back to stream ")
    SetStream()
    time.sleep(.05)
    PM1, PM25, PM10 = ReadSample()
    print("Stream sample", PM1, PM25, PM10)

    print(" Set to QA, fan OFF, get return code and sleep 10 seconds ")
    test_status = DormantMode("sleep")
    print(test_status)

    time.sleep(10)

    print(" Set to QA, fan ON ,get return code and sleep 10 seconds  ")
    test_status = DormantMode("run")
    print(test_status)

    time.sleep(10)

    PM1, PM25, PM10 = QAReadSample()
    print("Q&A take reading", PM1, PM25, PM10)

    time.sleep(2)

    PM1, PM25, PM10 = QAReadSample()
    print("Q&A take reading", PM1, PM25, PM10)

    time.sleep(2)

    PM1, PM25, PM10 = QAReadSample()
    print("Q&A take reading", PM1, PM25, PM10)

    SetStream()
    time.sleep(.1)
    PM1, PM25, PM10 = ReadSample()
    print("ReadSample output - loop end", PM1, PM25, PM10)
    time.sleep(.5)

    loopcount = loopcount + 1
    
########
#
#  End File
#