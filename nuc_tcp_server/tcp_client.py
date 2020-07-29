from socket import *
from struct import pack
import json

class ClientProtocol:

    def __init__(self):
        self.socket = None

    def connect(self, server_ip, server_port):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect((server_ip, server_port))

    def close(self):
        self.socket.shutdown(SHUT_WR)
        self.socket.close()
        self.socket = None

    def send_data(self, data):

        # use struct to make sure we have a consistent endianness on the length
        length = pack('>Q', len(data))

        # sendall to make sure it blocks if there's back-pressure on the socket
        self.socket.sendall(length)
        self.socket.sendall(data)

        ack = self.socket.recv(1)

        # could handle a bad ack here, but we'll assume it's fine.

if __name__ == '__main__':
    cp = ClientProtocol()
    data = {"one": 1, "two": "2", "three": [{"three?": "three!"}]}
    data = json.dumps(data)
    byte_data = data.encode("utf-8")
    print("len(data): {0}".format(len(data)))
    # cp.connect('192.168.2.109', 9999)
    cp.connect('127.0.0.1', 9999)
    cp.send_data(byte_data)
    cp.close()
