import socket
import struct
import time

s = socket.socket()
host = "192.168.1.57"
port = 1234
s.connect((host,port))
sm = s.makefile('b')
lasttime = 0
counter = 0
while True:
    if (time.time() - lasttime)>1:
        print(counter)
        counter = 0
        lasttime = time.time()
    data = sm.read(16)
    imuData = struct.unpack('<4f',data)
    counter += 1
    #print(imuData)