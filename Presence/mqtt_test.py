import paho.mqtt.client as mqtt
import time

def on_log(client, userdata, level, buf):
    print("log: ", buf)

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

#broker="broker.hivemq.com"
broker="39.109.156.167"
#port = 1883
port = 1884
#qos = 2
client = mqtt.Client("nyaastone1")
client.on_connect=on_connect
client.on_disconnect=on_disconnect
#client.on_log=on_log
client.on_message=on_message
print ("connecting to broker, ", broker)
client.connect(broker, port)

def send_message(msg)
    client.loop_start()
    start_time = time.localtime()
    print("I've connected, now sleeping")
    client.subscribe("haus/sensorz1")
    print("subscribed!")
    client.publish("haus/sensorz1", "mai_first_message, sent on " + start_time)
    client.publish("haus/sensorz1", "testing stuff, this is payload", qos=1) #testing QoS
    print("published!")
    time.sleep(20)
    print("wakey wakey")
    client.loop_stop()
#client.disconnect()