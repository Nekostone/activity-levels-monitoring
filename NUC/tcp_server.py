import json
import os
from socket import *
from struct import unpack
from os.path import exists
from RoomMonitor import ROOM_TYPES


class ServerProtocol:

    def __init__(self, output_dir):
        self.socket = None
        self.output_dir = output_dir
        self.file_numbers = {x : 0 for x in ROOM_TYPES}
	

    def listen(self, server_ip, server_port):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind((server_ip, server_port))
        self.socket.listen(1)

    def handle_data(self):
        try:
            while True:
                (connection, addr) = self.socket.accept()
                try:
                    bs = connection.recv(8)
                    (length,) = unpack('>Q', bs)
                    data = b''
                    while len(data) < length:
                        to_read = length - len(data)
                        received_data = connection.recv(
                            4096 if to_read > 4096 else to_read)
                        data += received_data

                    # send our 0 ack
                    assert len(b'\00') == 1
                    connection.sendall(b'\00')
                finally:
                    connection.shutdown(SHUT_WR)
                    connection.close()

                decoded_data = data.decode("utf-8")
                received_json = json.loads(decoded_data)
                print("received_json: {0}".format(received_json))
                print("type(received_json): {0}".format(type(received_json)))
                
                room_type = received_json["room_type"]
                del received_json["room_type"]
                self.file_numbers[room_type] += 1
                
                if not exists(room_type):
                    os.makedirs(room_type)
                    
                path_to_save = os.path.join(self.output_dir, room_type, str(self.file_numbers[room_type])) + ".json"
                print("saving to: ", path_to_save)
                with open(path_to_save, 'w+') as outfile:
                    json.dump(received_json, outfile)
                
        finally:
            print("closing port...")
            self.close()

    def close(self):
        self.socket.close()
        self.socket = None

        # could handle a bad ack here, but we'll assume it's fine.

if __name__ == '__main__':
    output_dir = "data"
    for x in ROOM_TYPES:
        foldername = os.path.join(output_dir,x)
        if not exists(foldername):
            os.makedirs(foldername)
    if not exists(output_dir):
        os.makedirs(output_dir)
    sp = ServerProtocol(output_dir)
    sp.listen('0.0.0.0', 9999)
    sp.handle_data()
