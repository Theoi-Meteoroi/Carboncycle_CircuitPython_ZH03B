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
       response = (hexlify(uart.read(3)))
       return("Fan OFF")

    #  Turn fan on
    #
    if pwr_status == "run":
       uart.reset_input_buffer()
       uart.write( b"\xFF\x01\xA7\x00\x00\x00\x00\x00\x58")
       #response = (hexlify(uart.read(14)))
       response = (hexlify(uart.read(3)))
       if response == b'ffa701':
          uart.reset_input_buffer()
          return ("Fan ON")
       elif response == b'ffa700':
          uart.reset_input_buffer()
          return ("Fan ERRoR?")


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
DormantMode(test_status)
SetStream()
print("ReadSample output - First iteration")
PM1,PM25,PM10=ReadSample()
print(PM1)
print(PM25)
print(PM10)
time.sleep(.5)

loopcount = 0

while test_status is not "ERROR":

    print("LoopCount=", loopcount)
    SetQA()
    print("Interrogate mode set")
    time.sleep(1)
    PM1, PM25, PM10 = QAReadSample()
    print("Interrogate - readsample", PM1, PM25, PM10)
    print(" Set back to streaming samples ")
    SetStream()
    time.sleep(1)
    
    PM1, PM25, PM10 = ReadSample()
    print(PM1, PM25, PM10)

    print(" Set to QA, fan OFF, sleep 5 seconds")
    test_status = DormantMode("sleep")
    print(test_status)
    time.sleep(5)

    print(" Set to QA, fan ON , sleep 5 seconds")
    test_status = DormantMode("run")
    print(test_status)
    time.sleep(5)

    PM1, PM25, PM10 = QAReadSample()
    print("Take single reading", PM1, PM25, PM10)

    time.sleep(2)

    PM1, PM25, PM10 = QAReadSample()
    print("Take single reading", PM1, PM25, PM10)

    time.sleep(2)

    PM1, PM25, PM10 = QAReadSample()
    print("Take single reading", PM1, PM25, PM10)

    SetStream()
    time.sleep(1)
    PM1, PM25, PM10 = ReadSample()
    print("ReadSample output - loop end", PM1, PM25, PM10)
    time.sleep(1)

    loopcount = loopcount + 1
    