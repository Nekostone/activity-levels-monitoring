import time
from   datetime import datetime
import serial
import numpy as np
import math
import pdb


BED_ROOM = "bedroom"
LIVING_ROOM = "livingroom"
KITCHEN = "kitchen"
OUTSIDE = "exit"
TOILET = "toilet"
ROOMS = [LIVING_ROOM, BED_ROOM, OUTSIDE, TOILET, KITCHEN]
VALID_TRANSITIONS = {
    BED_ROOM: [LIVING_ROOM, TOILET],
    LIVING_ROOM: [BED_ROOM, KITCHEN, OUTSIDE, TOILET],
    KITCHEN: [LIVING_ROOM],
    OUTSIDE: [LIVING_ROOM],
    TOILET: [LIVING_ROOM, BED_ROOM]
}

# used for connecting clients, subscribing and publishing to topics
BROKER = '192.168.0.102' 
PORT   = 1883
HOUSE_ID = "kjhouse"
DEVICE_TYPE = "NUC"
BPS_SENSOR = "bps"
MLX_SENSOR = "mlx"

from multiprocessing import Process, Manager
manager = Manager()
Global = manager.Namespace()

# to contain the status of all BPS in real time
binary_dict = manager.dict()
binary_dict = {
    BED_ROOM: 0,
    LIVING_ROOM: 0,
    KITCHEN: 0,
    OUTSIDE: 0,
    TOILET: 0
}
# if the person has stayed in a particular room for more than the cutoff time for that room, a notification is sent to the MQTT
ROOM_CUTOFF_TIME_MINUTES = {
    BED_ROOM: 60,
    LIVING_ROOM: 60,
    KITCHEN: 60,
    OUTSIDE: 60,
    TOILET: 60,
}
Global.last_visited = LIVING_ROOM
Global.last_entered_time = datetime.now()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print ("Connection OK!")
    else:
        print("Bad connection, Returned Code: ", rc)

def on_disconnect(client, userdata, flags, rc=0):
    print("Disconnected result code " + str(rc))

def on_message(client,userdata, msg):
    try:
        # print("while true - id(binary_dict): {0}".format(id(binary_dict)))
        topic=msg.topic
        device_type, house_id, current_room = topic.split("/")

        m_decode=str(msg.payload.decode("utf-8","ignore"))
        """
        print("-----")
        print("topic: {0}; m_decode: {1}".format(topic, m_decode))
        print("binary_dict: {0};".format(binary_dict))
        print("Global.last_entered_time: {0}".format(Global.last_entered_time))
        print("Global.last_visited: {0}".format(Global.last_visited))
        """
        if m_decode == "0" or m_decode == "1":
            binary_dict[current_room] = int(m_decode)

        # if the person has moved rooms
        if Global.last_visited != current_room and m_decode == "1":
            if is_valid_transition(current_room):
                print("nuc - person travels from {0} to {1}".format(Global.last_visited, current_room))
                Global.last_entered_time = datetime.now()
                Global.last_visited = current_room

                # activate respective MLX sensors according to the room where the person is in
                topic = "nuc/kjhouse"
                client.publish(topic, Global.last_visited)
                """
                for room in ROOMS:
                    topic = "/".join([MLX_SENSOR, HOUSE_ID, room])
                    if room == Global.last_visited:
                        client.publish(topic, "1")
                    else:
                        client.publish(topic, "0")
                """
                
    except Exception as e:
        print("ERROR: {0}".format(e))
        pdb.set_trace()

def is_valid_transition(current_room):
    return current_room in VALID_TRANSITIONS[Global.last_visited]

def mqtt_worker():

    # to run as a separate process
    import paho.mqtt.client as mqtt
    # MQTT Setup
    client = mqtt.Client()

    # Attach MQTT Client callback functions 
    client.on_connect    = on_connect
    client.on_disconnect = on_disconnect
    client.on_message    = on_message

    print("Connecting to broker...", BROKER)
    client.connect(BROKER, PORT)

    # Subscribe to topics for bps sensors
    for room in ROOMS:
        print("Subscribing to ", room)
        print("/".join([BPS_SENSOR, HOUSE_ID, room]))
        client.subscribe("/".join([BPS_SENSOR, HOUSE_ID, room]))

    client.publish("/".join([DEVICE_TYPE, HOUSE_ID, room]), "Started NUC!")
    client.loop_forever()

mqtt_worker_process = Process(target=mqtt_worker)
mqtt_worker_process.start()

while True:
    try:
        # print("binary_dict: {0}; Global.last_entered_time: {1}".format(binary_dict, Global.last_entered_time))
        cutoff_duration_minutes = ROOM_CUTOFF_TIME_MINUTES[Global.last_visited]
        current_duration = datetime.now()-Global.last_entered_time
        # print("binary_dict: {0}; current_duration(seconds): {1}; cutoff_duration_minutes: {2}".format(binary_dict, current_duration, cutoff_duration_minutes))
        if current_duration.total_seconds() >= cutoff_duration_minutes * 60:
            print("PONG")
            mqtt_worker_process.terminate()
            exit(0)
    except KeyboardInterrupt:
        print("Interrupt received.")
        mqtt_worker_process.terminate()
        exit(0)

