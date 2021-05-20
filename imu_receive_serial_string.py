#!/usr/bin/python -u
import threading, time
import socket
import struct
import ast
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import collections
import sys
import signal
import serial

def update(i):
    ay.cla()
    ap.cla()
    ar.cla()

    ay.plot(yaw)
    ay.scatter(len(yaw)-1, yaw[-1])
    ay.text(len(yaw)-1, yaw[-1]+2, "{}".format(yaw[-1]))
    ay.set_ylim(-200,200)

    ap.plot(pitch)
    ap.scatter(len(pitch)-1, pitch[-1])
    ap.text(len(pitch)-1, pitch[-1]+2, "{}".format(pitch[-1]))
    ap.set_ylim(-200,200)

    ar.plot(roll)
    ar.scatter(len(roll)-1, roll[-1])
    ar.text(len(roll)-1, roll[-1]+2, "{}".format(roll[-1]))
    ar.set_ylim(-200,200)

def recUDP():
    global yaw,pitch,roll
    t = threading.currentThread()
    port = 'COM11'
    baud = 115200
    ser = serial.Serial(port, baud, timeout=1)
    while getattr(t, "run", True):        
        data = ser.readline().decode().strip('\r\n')
        try:
            euler = [float(i) for i in data.split(',')]
            #print(euler)
            yaw.popleft()
            yaw.append(euler[0])
            pitch.popleft()
            pitch.append(euler[1])
            roll.popleft()
            roll.append(euler[2])
        except:
            print(data)    

def signal_handler(sig, frame):
    listen_UDP.run = False
    print("Stopped")

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
yaw = collections.deque(np.zeros(1200))
pitch = collections.deque(np.zeros(1200))
roll = collections.deque(np.zeros(1200))

listen_UDP = threading.Thread(target=recUDP)
listen_UDP.start()

ay = plt.subplot(311)
ap = plt.subplot(312)
ar = plt.subplot(313)
plt.gcf().set_size_inches(20,10)
ani = FuncAnimation(plt.gcf(), update, interval=20)
plt.show()
print ("Done")
listen_UDP.run = False
listen_UDP.join