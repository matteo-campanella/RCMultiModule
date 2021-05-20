#!/usr/bin/python -u
import socketserver, threading, time
import socket
import struct
import fifo

class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        global buffer
        data = self.request[0]
        socket = self.request[1]
        #current_thread = threading.current_thread()
        #print("{}: client: {}, wrote: {}".format(current_thread.name, self.client_address, data))
        #socket.sendto(data.upper(), self.client_address)
        buffer.write(data)

class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass
 
if __name__ == "__main__":
    host = "0.0.0.0"
    port = 1234
    buffer = fifo.BytesFIFO(1024)

    server = socketserver.ThreadingUDPServer((host, port), ThreadedUDPRequestHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True

    status = 0

    try:
        server_thread.start()
        print("Server started at {} port {}".format(host, port))
        while True: 
            if not(buffer.empty()):
                print(buffer.read(1))

    except (KeyboardInterrupt, SystemExit):
        server.shutdown()
        server.server_close()
        exit()

# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.bind((host, port))

# sm = sock.makefile('b')
# lasttime = 0
# counter = 0
# while True:
#     #if (time.time() - lasttime)>1:
#     #    print(counter)
#     #    counter = 0
#     #    lasttime = time.time()
#     data = sm.read(6)
#     imuData = struct.unpack('<3H',data)
#     #counter += 1
#     print(imuData)