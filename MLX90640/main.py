import asyncio
import math
import sys
import time
from multiprocessing import Process, Queue

import numpy as np
import paho.mqtt.client as mqtt
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

import queue

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
        print("publishing message to: {}".format(topic))
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

def collect_data(data, start_time):
    frame = [0] * 768
    counter = 0
    while True:
        try:
            mlx.getFrame(frame)  #  get the mlx values and put them into the array we just created
            array = np.array(frame) 
            if array.shape[0] == ARRAY_SHAPE[0] * ARRAY_SHAPE[1]:
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
    global data_collection_process

    m_decode=str(msg.payload.decode("utf-8","ignore"))
    
    # debug message
    print("=============================")
    print("message received for {}!".format(RPI_ROOM_TYPE))
    print("msg: {0}".format(m_decode))
    
    # check topic
    topic=msg.topic
    print("Topic: " + topic)
    sensor_type, house_id, room_type = topic.split("/")
    print("Sensor Type: {}, House_ID: {}, Room_Type: {}".format(sensor_type, house_id, room_type))
 
    # check decoded message content and change current MLX shown
    if m_decode == "0" and room_type == RPI_ROOM_TYPE:
        if data_collection_process:
            data_collection_process.terminate()
            end_time = time.strftime("%Y.%m.%d_%H%M%S",time.localtime(time.time()))
            collected_data = []
            while not data.empty():
                try:
                    collected_data.append(data.get())
                except Exception as e:
                    print(e)
                    break
            # print("Sending data array of length: {}".format(len(data)))
            try:
                start_time = data_times.get()
                print("Data collection started at {}, and ended at {}".format(start_time,end_time))
                analysis_result = displacement_history(collected_data, start_time, end_time)
                analysis_result["room_type"] = RPI_ROOM_TYPE
                print(analysis_result)
                to_send = json.dumps(analysis_result)
                
                #to_send = json.dumps({'test':len(collected_data)})
                byte_data = to_send.encode("utf-8")
                cp.connect(broker, 9999)
                print("len(byte_data): {0}".format(len(byte_data)))
                cp.send_data(byte_data)
                cp.close()
                
                start_time = None
                end_time = None
            except Exception as e:
                print(e)
    
            print("Resetted data array, now length: {}".format(collected_data.qsize()))
    elif m_decode == "1" and room_type == RPI_ROOM_TYPE:
        # spawns parallel process to write sensor data to .npy files
        start_time = time.strftime("%Y.%m.%d_%H%M%S",time.localtime(time.time()))
        data_times.put(start_time)
        data_collection_process = Process(target=main.collect_data, args=(data, data_times))
        data_collection_process.start()
    
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print ("Connection OK!")
    else:
        print("Bad connection, Returned Code: ", rc)

def on_disconnect(client, userdata, flags, rc=0):
    print("Disconnected result code " + str(rc))


BAUD_RATE = 115200
ARRAY_SHAPE = (24, 32)

broker = "13.229.212.221"
port = 1883

i2c = busio.I2C(board.SCL, board.SDA, frequency=400000) # setup I2C
mlx = adafruit_mlx90640.MLX90640(i2c) # begin MLX90640 with I2C comm
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ # set refresh 
print("set up mlx to i2c")  
cp = ClientProtocol()
data = Queue()
data_times = Queue()

if True:
    try: 
        mqttclient = MQTTClient(broker, port)
        mqttclient.subscribe(topic="NUC/kjhouse/bedroom")
    except Exception as e:
        print(e)
    RPI_ROOM_TYPE = "bedroom"
    mqttclient.client.on_connect = on_connect
    mqttclient.client.on_disconnect = on_disconnect
    mqttclient.client.on_message = on_message  # makes it so that the callback on receiving a message calls on_message() above
    
    try:
        mqttclient.client.publish("/".join(["Rpi", "kjhouse", RPI_ROOM_TYPE]), "Rpi operational!")
        mqttclient.client.loop_forever()
    except InterruptedError as e:
        if data_collection_process:
            data_collection_process.terminate()        
    except Exception as e:
        print(e)

