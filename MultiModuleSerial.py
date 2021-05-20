# ©2021 Matteo Campanella 
import serial as s
import numpy as np
import threading
import logging
import time
import signal
import sys
import os

buffer = np.zeros(36,dtype=np.uint8)
buffer[0]= 0x55
buffer[1]= 10
buffer[2]= 0

threadStopped = False
readyToSend = False

ser = None

a = 974
e = 974
t = 147
r = 1024

def signal_handler(sig, frame):
    global threadStopped
    print('Stopping Thread')
    threadStopped = True

def initSerial(port):
    global ser 
    ser = s.Serial(port, 100000, timeout=1, bytesize=s.EIGHTBITS, parity=s.PARITY_EVEN, stopbits=s.STOPBITS_TWO)

def setProtocol(protocol):
    protocol = protocol & 0b00111111
    if (protocol < 31):
        buffer[0] = 0x55
    else:
        buffer[0] = 0x54
    protocol = protocol & 0b00011111
    buffer[1] = (buffer[1] & 0b11100000) | protocol
    logging.debug("buffer1 {0:b}".format(buffer[1]))

def setBindBits(bindBit,rangeCheckBit,autoBindBit):
    buffer[1] = (buffer[1] & 0b00011111) | (bindBit * 0x80) | (rangeCheckBit * 0x40) | (autoBindBit * 0x20)
    logging.debug("buffer1 {0:08b}".format(buffer[1]))

def setLowPower(lowPowerBit):
    buffer[2] = (buffer[2] & 0b01111111) | (lowPowerBit * 0x80)
    logging.debug("buffer2 {0:08b}".format(buffer[2]))

def setSubProtocol(subProtocol):
    buffer[2] = (buffer[2] & 0b10001111) | ((subProtocol & 0x07) << 4)
    logging.debug("buffer2 {0:08b}".format(buffer[2]))

def setOptionProtocol(optionProtocol):
    buffer[3] = optionProtocol
    logging.debug("buffer3 {0:08b}".format(buffer[3]))

def setRxNum(rxNum):
    buffer[2] = (buffer[2] & 0b11110000) | (rxNum & 0x0f)
    logging.debug("{0:08b}".format(buffer[2]))    

def setLowPower():
    buffer[2] = (buffer[2] & 0b01111111) | 0x80
    logging.debug("{0:08b}".format(buffer[2]))  

def setChannel(channelNo,channelValue):
    #byte 4 to 25 (22 bytes) - 16 channels on 11 bits
    channelValue = channelValue & 0b11111111111
    channels = getChannels()
    channels[channelNo-1]=channelValue
    setChannels(channels)

def setChannels(channels):
    global buffer
    channelBits = np.zeros(16*11,dtype = np.uint8)
    for channel in range(16):
        for bit in range(11):
            channelBits[channel*11+bit] = channels[channel] & 0x01
            channels[channel] = channels[channel] >> 1         
    buffer[4:26] = np.packbits(channelBits,None,bitorder='little')            
    print(buffer)

def getChannels():
    #byte 4 to 25 (22 bytes) - 16 channels on 11 bits
    channels = np.zeros(16,dtype = np.uint16)
    channelBits = np.unpackbits(buffer[4:26],None,bitorder='little')
    for channel in range(16):
        for bit in range(11):
            channels[channel] = channels[channel] | (channelBits[channel*11+bit] << bit)
    return channels

def toggleReadyToSend():
    global readyToSend
    readyToSend = not readyToSend

def sendPacket(delay):
    global ser
    while (not threadStopped):
        if readyToSend:
            ser.write(buffer)
        time.sleep(delay)
    logging.debug("Thread Exiting")        

logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
signal.signal(signal.SIGINT, signal_handler)

initSerial('COM8')
x = threading.Thread(target=sendPacket, args=(.02,))
x.start()

setProtocol(10)
setLowPower()
setBindBits(1,0,0)
toggleReadyToSend()
time.sleep(3)

toggleReadyToSend()
setBindBits(0,0,0)
toggleReadyToSend()
time.sleep(5)

toggleReadyToSend()
setChannel(1,a)
setChannel(2,e)
setChannel(3,t)
setChannel(4,r)
toggleReadyToSend()

while (not threadStopped):
    c = input(':')
    if c == 'e':
        e = e+50
    if c == 'E':
        e=e-50
    if c == 'r':
        r = r+50
    if c == 'R':
        r = r-50
    if c == 't':
        t = t+50
    if c == 'T':
        t = t-50
    if c == 'a':
        a = a+50
    if c == 'A':
        a = a-50
    toggleReadyToSend()
    setChannel(1,a)
    setChannel(2,e)
    setChannel(3,t)
    setChannel(4,r)
    toggleReadyToSend()
    print(a,e,t,r)
