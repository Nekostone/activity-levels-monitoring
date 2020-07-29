import time
from   datetime import datetime
import paho.mqtt.client as mqtt
import serial

from RoomMonitor import RoomMonitor, LIVING_ROOM, BED_ROOM, KITCHEN, TOILET, OUTSIDE

def bitfield(n):
    return [1 if digit=='1' else 0 for digit in bin(n)[2:]]

def Log2(x): 
    return (math.log10(x) / math.log10(2))
    
def isPowerOfTwo(n): 
    return (math.ceil(Log2(n)) == math.floor(Log2(n)))

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print ("Connection OK!")
    else:
        print("Bad connection, Returned Code: ", rc)

def on_disconnect(client, userdata, flags, rc=0):
    print("Disconnected result code " + str(rc))

def on_message(client,userdata, msg):
    topic=msg.topic
    
    print("=============================") # debug message
    print("message received!")
    m_decode=str(msg.payload.decode("utf-8","ignore"))
    print("msg: {0}".format(m_decode))
    
    device_type, house_id, room_type = topic.split("/")
    print("Device Type: {}, House_ID: {}, Room_Type: {}".format(device_type, house_id, room_type))


    if m_decode == "0" or m_decode == "1":
        binary_dict[room_type] = int(m_decode)
        state_value = 0
        for x in weight_dict:
            state_value += weight_dict[x] * binary_dict[x]
        if isPowerOfTwo(state_value):
            for x in binary_dict:
                if x == room_type:
                    binary_dict[x] = 1
                else:
                    binary_dict[x] = 0
        print(binary_dict)
    print("=============================")
    
    
def send_msg_if_room_changed(state_value: int, last: str, topic: str, state_machine):
    if state_value == 1:
        new = 'Bedroom'
    elif state_value == 2:
        new = 'Living Room'
    elif state_value == 4:
        new = 'Kitchen'
    elif state_value == 8:
        new = 'Toilet'
    elif state_value == 16:
        new = 'Not home'
    else:
        return last, False

    if last == 'Bedroom' and new == 'Toilet':
        state_machine.bed2toilet()
    elif last =='Toilet' and new == 'Bedroom':
        state_machine.toilet2bed()
    elif last == 'Bedroom' and new == 'Living Room':
        state_machine.bed2liv()
    elif last == 'Living Room' and new == 'Bedroom':
        statemachine.liv2bed()
    elif last == 'Living Room' and new == 'Toilet':
        statemachine.liv2toilet()
    elif last == 'Toilet' and new == 'Living Room':
        statemachine.toilet2liv()
    elif last == 'Living Room' and new == 'Not home':
        statemachine.liv2out()
    elif last == 'Not home' and new == 'Living Room':
        statemachine.out2liv()

    print(state_machine.current_state.name)
    client.publish(topic, state_machine.current_state.name)
    last = new
    return last, True

# MQTT Setup
client_name = "swcannotconnecthalp" 
client = mqtt.Client(client_name)

# Connect to broker
BROKER = '39.109.156.167' 
PORT   = 1884 

# Attach MQTT Client callback functions 
client.on_connect    = on_connect
client.on_disconnect = on_disconnect
client.on_message    = on_message

print("Connecting to broker...", BROKER)
client.connect(BROKER, PORT)
client.loop_start()

# Subscribe to topics
HOUSE_ID = "kjhouse"
DEVICE_TYPE = "NUC"
sensors = ["bps", "mlx"]
topics = [LIVING_ROOM, BED_ROOM, OUTSIDE, TOILET, KITCHEN]

for sensor in sensors:
    for topic in topics:
        print("Subscribing to ", topic)
        client.subscribe("/".join(sensor, HOUSE_ID, topic))

client.publish("/".join(DEVICE_TYPE, HOUSE_ID, topic), "Started NUC!")

# State Machine and monitoring setup
state_machine  = RoomMonitor()
print("original state :", state_machine.current_state)
initial_room = state_machine.current_state.name
last_visited = initial_room

print("Monitoring Presence...")
weight_arr = [BED_ROOM, LIVING_ROOM, KITCHEN, OUTSIDE, TOILET]
weight_dict = {weight_arr[i] : 2**i for i in range(5)} 
binary_dict = {weight_arr[i] : 0 for i in range(5)}
    
while True:
    try:
        last_visited, room_changed = send_msg_if_room_changed(x, last_visited, topic, state_machine)
        
    except ValueError:
        print("Invalid string")
