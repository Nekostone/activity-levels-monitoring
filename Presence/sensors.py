import serial
import time
from presence import RoomMonitor
import paho.mqtt.client as mqtt

def bitfield(n):
    return [1 if digit=='1' else 0 for digit in bin(n)[2:]]

def on_log(client, userdata, level, buf):
    print("log: ", buf)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print ("Connection OK!")
    else:
        print("Bad connection, Returned Code: ", rc)

def on_disconnect(client, userdata, flags, rc=0):
    print("Disconnected result code " + str(rc))

def send_message(msg: str, topic: str):
    client.loop_start()
    start_time = time.localtime()
    print("I've connected, now sleeping")
    client.subscribe("haus/sensorz1")
    print("subscribed!")
    client.publish(topic, "mai_first_message, sent on " + start_time)
    client.publish(topic, msg, qos=1) #testing QoS
    print("published!")
    time.sleep(20)
    print("wakey wakey")
    client.loop_stop()

def on_message(client,userdata, msg):
    topic=msg.topic
    m_decode=str(msg.payload.decode("utf-8","ignore"))
    print("message received! =>", m_decode)

# MQTT Setup
broker = '39.109.156.167'
port   = 1884
client = mqtt.Client("nyaastone1")

client.on_connect    = on_connect
client.on_disconnect = on_disconnect
client.on_message    = on_message

print ("connecting to broker, ", broker)
client.connect(broker, port)
client.subscribe("haus/sensorz1")

# State Machine and monitoring setup
state  = RoomMonitor()
living = serial.Serial('COM11', 57600)
last = 'Living Room'

print("Monitoring...")
while True:
    val = living.readline()
    x   = val.decode('utf-8', errors="ignore").strip()

    try:
        x = int(x)
        # Room presence values given as bit vector ['Bedroom', 'Living Room']
        
        if x//2 == 1:
            new = 'Bedroom'
            if last == 'Living Room' and new == 'Bedroom': # change state if last value different from current
                state.liv2bed()
                print(state.current_state.name)
                client.publish("haus/sensorz1", state.current_state.name)
                last = 'Bedroom'
        elif x == 1:
            new = 'Living Room'
            if last == 'Bedroom' and new == 'Living Room': # change state if last value different from current
                state.bed2liv()
                print(state.current_state.name)
                client.publish("haus/sensorz1", state.current_state.name)
                last = 'Living Room'
        else:
            None
    except ValueError:
        print("Weird string")

