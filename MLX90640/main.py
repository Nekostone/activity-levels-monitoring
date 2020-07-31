import asyncio
import math
import sys
import time
import pdb
from multiprocessing import Process, Queue

import numpy as np
import serial

import adafruit_mlx90640
import board
import busio
import main
from file_utils import create_folder_if_absent, save_npy
from visualizer import init_heatmap, update_heatmap
from centroid_history import displacement_history
from socket import *
from struct import pack
import json


# load config
import os
import sys
curr_dir = os.path.dirname(os.path.realpath(__file__))
config_dir = os.path.join(curr_dir, "config.json")
with open(config_dir, "r") as readfile:
    global config
    config = json.loads(readfile.read())

BAUD_RATE = 115200
ARRAY_SHAPE = (24, 32)
TCP_addr = config["mlx_nuc_ip_to_send_json"]
broker = config["mqtt_broker_ip"]
port = config["mqtt_broker_port"]
RPI_ROOM_TYPE = config["room_type"]

data_collection_process = None  # placeholder to contain process that colelcts data

i2c = busio.I2C(board.SCL, board.SDA, frequency=400000) # setup I2C
mlx = adafruit_mlx90640.MLX90640(i2c) # begin MLX90640 with I2C comm
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ # set refresh 
data = Queue()
data_times = Queue()


class ClientProtocol:

    def __init__(self):
        self.socket = None

    def connect(self, server_ip, server_port):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect((server_ip, server_port))
        print("Connected to TCP Server")

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

cp = ClientProtocol()

def interpolate_values(df):
    """
    :param: 24x32 data frame obtained from get_nan_value_indices(df)
    :return: 24x32 array
    """
    nan_value_indices = np.argwhere(np.isnan(df))
    x_max = df.shape[0] - 1
    y_max = df.shape[1] - 1
    for indx in nan_value_indices:
        x = indx[0]
        y = indx[1]
        if x == 0 and y == 0:
            df[x][y] = (df[x + 1][y] + df[x][y + 1]) / 2

        elif (x == x_max and y == y_max):
            df[x][y] = (df[x - 1][y] + df[x][y - 1]) / 2

        elif (x == 0 and y == y_max):
            df[x][y] = (df[x + 1][y] + df[x][y - 1]) / 2

        elif (x == x_max and y == 0):
            df[x][y] = (df[x - 1][y] + df[x][y + 1]) / 2

        elif (x == 0):
            df[x][y] = (df[x + 1][y] + df[x][y - 1] + df[x][y + 1]) / 3

        elif (x == x_max):
            df[x][y] = (df[x - 1][y] + df[x][y - 1] + df[x][y + 1]) / 3

        elif (y == 0):
            df[x][y] = (df[x + 1][y] + df[x - 1][y] + df[x][y + 1]) / 3

        elif (y == y_max):
            df[x][y] = (df[x - 1][y] + df[x + 1][y] + df[x][y - 1]) / 3
        else:
            df[x][y] = (df[x][y + 1] + df[x + 1][y] + df[x - 1][y] + df[x][y - 1]) / 4
    return df

def collect_data(data):
    frame = [0] * 768
    counter = 0
    while True:
        try:
            mlx.getFrame(frame)  #  get the mlx values and put them into the array we just created
            array = np.array(frame) 
            if np.sum(array) > 0:
                df = np.reshape(array.astype(float), ARRAY_SHAPE)
                df = interpolate_values(df)
                data.put(df)
                print("Frame collected [{}]".format(counter))
                counter += 1
        except ValueError:
            # these happen, no biggie - retry
            print("ValueError during data collection")
            pass
        except InterruptedError:
            pass
            # print("Stopping data collection..., num frames collected: {}".format(len(data)))
    
def on_message(client,userdata, msg):
    try:
        global data_collection_process
        m_decode=str(msg.payload.decode("utf-8","ignore"))
       
        """ 
        # debug message
        print("=============================")
        print("message received for {}!".format(RPI_ROOM_TYPE))
        print("msg: {0}".format(m_decode))
        """
        
        # check topic
        topic=msg.topic
        # print("Topic: " + topic)
        sensor_type, house_id = topic.split("/")
        # print("Sensor Type: {}, House_ID: {}".format(sensor_type, house_id))
     
        # print("data_collection_process: {0}".format(data_collection_process))
        # check decoded message content and change current MLX shown
        if m_decode == RPI_ROOM_TYPE and not data_collection_process:
            print("start mlx collection")
            # spawns parallel process to write sensor data to .npy files
            start_time = time.strftime("%Y.%m.%d_%H%M%S",time.localtime(time.time()))
            data_times.put(start_time)
            data_collection_process = Process(target=main.collect_data, args=(data, ))
            data_collection_process.start()
        elif data_collection_process:
            print("end mlx collection")
            data_collection_process.terminate()
            data_collection_process = None
            end_time = time.strftime("%Y.%m.%d_%H%M%S",time.localtime(time.time()))
            collected_data = []
            while not data.empty():
                try:
                    collected_data.append(data.get())
                except Exception as e:
                    print(e)
                    break
            # print("Sending data array of length: {}".format(len(data)))
            start_time = data_times.get()
            print("Data collection started at {}, and ended at {}".format(start_time,end_time))
            # pdb.set_trace()
            print("len(collected_data): {0}".format(len(collected_data)))
            if len(collected_data) != 0:
                analysis_result = displacement_history(collected_data, start_time, end_time)
                analysis_result["room_type"] = RPI_ROOM_TYPE
                print("analysis_result: {0}".format(analysis_result))
                to_send = json.dumps(analysis_result)
                byte_data = to_send.encode("utf-8")
                cp.connect(TCP_addr, config["mlx_nuc_port_to_send_json"])
                print("len(byte_data): {0}".format(len(byte_data)))
                cp.send_data(byte_data)
                cp.close()
                
                start_time = None
                end_time = None
       
                collected_data.clear() 
                print("Resetted data array, now length: {}".format(len(collected_data)))
    except InterruptedError:
        if data_collection_process:
            data_collection_process.terminate()
            exit(0)
    except Exception as e:
        print(e)
        pdb.set_trace()

    
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print ("Connection OK!")
    else:
        print("Bad connection, Returned Code: ", rc)

def on_disconnect(client, userdata, flags, rc=0):
    print("Disconnected result code " + str(rc))




import paho.mqtt.client as mqtt
client = mqtt.Client()
client.connect(config["mqtt_broker_ip"], config["mqtt_broker_port"])
client.subscribe(topic=config["mlx_topic_to_listen"])
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message  # makes it so that the callback on receiving a message calls on_message() above
client.publish(config["mlx_topic_to_publish"], "Rpi operational!")

try:
    client.loop_forever()
except Exception as e:
    print(e)
"""
except InterruptedError as e:
    if data_collection_process:
        data_collection_process.terminate()
"""

