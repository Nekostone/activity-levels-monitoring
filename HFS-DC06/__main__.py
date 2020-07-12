import time

import paho.mqtt.client as mqtt
import serial

from RoomMonitor import RoomMonitor, LIVING_ROOM, BED_ROOM, KITCHEN, TOILET, OUTSIDE


def bitfield(n):
    return [1 if digit=='1' else 0 for digit in bin(n)[2:]]

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print ("Connection OK!")
    else:
        print("Bad connection, Returned Code: ", rc)

def on_disconnect(client, userdata, flags, rc=0):
    print("Disconnected result code " + str(rc))

def on_message(client,userdata, msg):
    topic=msg.topic
    m_decode=str(msg.payload.decode("utf-8","ignore"))
    print("message received! =>", m_decode)
    
def send_msg_if_room_changed(serial_output: int, room1: str, room2: str, last: str, topic: str, state_machine):
    if serial_output//2 == 1:
        new = room2
        if last == room1 and new == room2: # change state if last value different from current
            state_machine.liv2bed()
            print(state_machine.current_state.name)
            client.publish(topic, state_machine.current_state.name)
            last = room2
    elif serial_output == 1:
        new = room1
        if last == room2 and new == room1: # change state if last value different from current
            state_machine.bed2liv()
            print(state_machine.current_state.name)
            client.publish(topic, state_machine.current_state.name)
            last = room1
    else:
        return last, False
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

# Subscribe to topic
SENSOR_TYPE = "bps"
HOUSE_ID = "kjhaus"
ROOMTYPE = BED_ROOM
topic = "/".join([SENSOR_TYPE, HOUSE_ID, ROOMTYPE])
print("Subscribing to ", topic)
client.subscribe(topic)

client.publish(topic, "test intro")

# State Machine and monitoring setup
state_machine  = RoomMonitor()
print("original state :", state_machine.current_state)
ser = serial.Serial('COM11', 57600)
initial_room = state_machine.current_state.name
last_visited = initial_room

if __name__ == "__main__":
    print("Monitoring Presence...")
    while True:
        val = ser.readline()
        x   = val.decode('utf-8', errors="ignore").strip()
        try:
            x = int(x)
            # Room presence values given as bit vector ['Bedroom', 'Living Room']
            last_visited, room_changed = send_msg_if_room_changed(x, initial_room, ROOMTYPE, last_visited, topic, state_machine)
            
        except ValueError:
            print("Invalid string")
