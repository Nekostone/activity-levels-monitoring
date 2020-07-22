from socket import *
from struct import pack
import pickle
import numpy as np


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

    data = None
    data = np.array([[1,2,3],[4,5,6],[7,8,9]])
    data = pickle.dumps(data)
    """
    with open('/home/catstone/Desktop/to_send.txt', 'rb') as fp:
        data = fp.read()

    assert(len(data))
    """
    cp.connect('192.168.2.109', 9999)
    cp.send_data(data)
    cp.close()
