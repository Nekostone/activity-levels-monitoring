import time
import paho.mqtt.client as mqtt
import numpy as np
import serial
from file_utils import save_npy, create_folder_if_absent
from visualizer import init_heatmap, update_heatmap
import asyncio
import math

import main
from multiprocessing import Process
import sys

"""
Initialization
Serial Parameters - Port, Baud Rate, Start Byte
Program Mode - Plot (Debug) / Write Mode
"""

# SERIAL_PORT = 'COM3'  # for windows
# SERIAL_PORT = "/dev/ttyS3" # for linux
BAUD_RATE = 115200
ARRAY_SHAPE = (24, 32)

DEBUG_MODE = 1
WRITE_MODE = 0
DATA_PATH = "data/switching test"  # change as it fits
DATA_DIR_SORT = "day"
broker = "192.168.2.109"
port = 1883
mlx_number = 0


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

def handle_df(values, counter, write=False):
    array = np.array(values)
    if array.shape[0] == ARRAY_SHAPE[0] * ARRAY_SHAPE[1]:
        df = np.reshape(array.astype(float), ARRAY_SHAPE)
        df = interpolate_values(df)
        if write: 
            save_npy(df, DATA_PATH, directory_sort=DATA_DIR_SORT)

        return df, True
    else:
        return None, False
        
def update_plot(decoded_values, counter):
    df, legit_string = handle_df(decoded_values, counter)

    if legit_string:
        print("Updating Heatmap...", "[{}]".format(counter))
        update_heatmap(df, plot)
    else:
        print("Not Updating Heatmap...", "[{}]".format(counter))

def save_serial_output(ser, counter, plot, mlx_number=0):
    """
    Save serial output from arduino
    """
    if mlx_number == 0:
        ser.port = 'COM3' # CHANGE THIS
    elif mlx_number == 1:
        ser.port = 'COM7' # CHANGE THIS

    try:
        ser_bytes = ser.readline()
        decoded_string = ser_bytes.decode("utf-8", errors='ignore').strip("\r\n")
        values = decoded_string.split(",")[:-1]
        update_plot(values)

    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(e)
        
def Log2(x): 
    return (math.log10(x) / math.log10(2))
    
def isPowerOfTwo(n): 
    return (math.ceil(Log2(n)) == math.floor(Log2(n)))

def on_message(client,userdata, msg):
    global mlx_number
    global write_to_npy_process

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
    if m_decode == "0":
        binary_dict[room_type] = int(m_decode)
        mlx_number = 0
        print("MLX now: ", + mlx_number)
        if write_to_npy_process:
            write_to_npy_process.terminate()
    elif m_decode == "1":
        binary_dict[room_type] = int(m_decode)
        mlx_number = 1
        print("MLX now: ", + mlx_number)
        # spawns parallel process to write sensor data to .npy files
        write_to_npy_process = Process(target=main.save_serial_output, args = (True,), kwargs={"mode":1,}) 
        write_to_npy_process.start()
    
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


# if __name__ == "__main__":  #REMEMBER TO CHANGE THIS NAME LOLOL IT WONT RUN IF THIS NAME DOESNT MATCH THE FILENAME
if True:
    min_temp = 28
    max_temp = 40
    # plot = init_heatmap("MLX90640 Heatmap", ARRAY_SHAPE, min_temp, max_temp)
    # ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    # ser.reset_output_buffer()
    
    # if mode == WRITE_MODE:
    #     create_folder_if_absent(DATA_PATH)
    
    BED_ROOM = "bedroom"
    LIVING_ROOM = "livingroom"
    KITCHEN = "kitchen"
    OUTSIDE = "nothome"
    TOILET = "toilet"
    
    weight_arr = [BED_ROOM, LIVING_ROOM, KITCHEN, OUTSIDE, TOILET]
    weight_dict = {weight_arr[i] : 2**i for i in range(5)} 
    binary_dict = {weight_arr[i] : 0 for i in range(5)} 

    print("Start weight dictionary:")
    print(weight_dict)
    
    mqttclient = MQTTClient(broker, port)
    mqttclient.subscribe(topic="bps/kjhouse")
    mqttclient.subscribe(topic="bps/kjhouse/livingroom")
    mqttclient.subscribe(topic="bps/kjhouse/bedroom")
    mqttclient.client.on_connect = on_connect
    mqttclient.client.on_disconnect = on_disconnect
    mqttclient.client.on_message = on_message  # makes it so that the callback on receiving a message calls on_message() above
    mqttclient.client.loop_start()

    while True:
        pass
        # === serial format
        # save_serial_output(ser, counter, plot, mlx_number)
        
        # === get from esp format
        # values = getfromsomewhere?
        # update_plot(decoded_values=values)

    mqttclient.client.loop_stop()
    # client.disconnect()
