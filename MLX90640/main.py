import asyncio
import math
import sys
import time
from multiprocessing import Process

import numpy as np
import paho.mqtt.client as mqtt
import serial

import adafruit_mlx90640
import board
import busio
import main
from file_utils import create_folder_if_absent, save_npy
from visualizer import init_heatmap, update_heatmap
from presence_detection import analyze_centroid_displacement_history
from socket import *
from struct import pack
import json

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

        # could handle a bad ack here, but we'll assume it's fine.


class MQTTClient:
    def __init__(self, broker, port):

        client = mqtt.Client("teck0")
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        print("connecting to broker, ", broker)
        client.connect(broker, port)
        self.client = client
    def subscribe(self, topic):
        self.client.subscribe(topic)
        print("Subscribed to topic:", topic)
    def send_message(self, msg, topic):
        self.client.publish(topic, msg)

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

def collect_data():
    global data
    frame = [0] * 768
    while True:
        try:
            mlx.getFrame(frame)  #  get the mlx values and put them into the array we just created
            array = np.array(frame) 
            if array.shape[0] == ARRAY_SHAPE[0] * ARRAY_SHAPE[1]:
                df = np.reshape(array.astype(float), ARRAY_SHAPE)
                df = interpolate_values(df)
                data.append(df)
        except ValueError:
            # these happen, no biggie - retry
            print("ValueError during data collection")
            pass
        except InterruptedError:
            print("Stopping data collection...")
    

def Log2(x): 
    return (math.log10(x) / math.log10(2))
    
def isPowerOfTwo(n): 
    return (math.ceil(Log2(n)) == math.floor(Log2(n)))

def on_message(client,userdata, msg):
    global data
    global data_collection_process

    m_decode=str(msg.payload.decode("utf-8","ignore"))
    
    # debug message
    print("=============================")
    print("message received!")
    print("msg: {0}".format(m_decode))
    
    # check topic
    topic=msg.topic
    print("Topic: " + topic)
    sensor_type, house_id, room_type = topic.split("/")
    print("Sensor Type: {}, House_ID: {}, Room_Type: {}".format(sensor_type, house_id, room_type))
 
    # check decoded message content and change current MLX shown
    if m_decode == "0" and room_type == RPI_room_type:
        binary_dict[room_type] = int(m_decode)
        if data_collection_process:
            data_collection_process.terminate()
            to_send = json.dumps(data)
            byte_data = to_send.encode("utf-8")
            cp.connect(broker, 9999)
            cp.send_data(byte_data)
            cp.close()
    
            data = []
            print("Resetted data array")
    elif m_decode == "1" and room_type == RPI_room_type:
        binary_dict[room_type] = int(m_decode)
        # spawns parallel process to write sensor data to .npy files
        data_collection_process = Process(target=main.collect_data) 
        data_collection_process.start()
        print("Data collection started")
    
    state_value = 0
    for x in weight_dict:
        state_value += weight_dict[x] * binary_dict[x]
        
    
    if isPowerOfTwo(state_value):
        for x in binary_dict:
            if x == room_type:
                binary_dict[x] = 1
            else:
                binary_dict[x] = 0
    
    print("Dictionary: ")
    print(binary_dict)
    print("=============================")
 
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print ("Connection OK!")
    else:
        print("Bad connection, Returned Code: ", rc)

def on_disconnect(client, userdata, flags, rc=0):
    print("Disconnected result code " + str(rc))


BAUD_RATE = 115200
ARRAY_SHAPE = (24, 32)

broker = "192.168.0.102"
port = 1883

i2c = busio.I2C(board.SCL, board.SDA, frequency=400000) # setup I2C
mlx = adafruit_mlx90640.MLX90640(i2c) # begin MLX90640 with I2C comm
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ # set refresh 
print("set up mlx to i2c")  
cp = ClientProtocol()
data = []

if True:
    BED_ROOM = "bedroom"
    LIVING_ROOM = "livingroom"
    KITCHEN = "kitchen"
    OUTSIDE = "outside"
    TOILET = "toilet"

    RPI_room_type = BED_ROOM
    weight_arr = [BED_ROOM, LIVING_ROOM, KITCHEN, OUTSIDE, TOILET]
    weight_dict = {weight_arr[i] : 2**i for i in range(5)} 
    binary_dict = {weight_arr[i] : 0 for i in range(5)} 

    print("Start weight dictionary:")
    print(weight_dict)

    try: 
        mqttclient = MQTTClient(broker, port)
        mqttclient.subscribe(topic="bps/kjhouse")
        mqttclient.subscribe(topic="bps/kjhouse/livingroom")
        mqttclient.subscribe(topic="bps/kjhouse/bedroom")
    except Exception as e:
        print(e)
    mqttclient.client.on_connect = on_connect
    mqttclient.client.on_disconnect = on_disconnect
    mqttclient.client.on_message = on_message  # makes it so that the callback on receiving a message calls on_message() above
    
    try:
        mqttclient.client.loop_forever()
    except InterruptedError as e:
        if data_collection_process:
            data_collection_process.terminate()        

