#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>

const char* ssid = "Doggie";
const char* password = "@lph@numer!c";

const char* mqtt_server = "192.168.2.103";

WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
int value = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200); //Start Serial
  int sensorPin = 17;
  setup_wifi();//Connection function is written below
  client.setServer(mqtt_server, 1883);// Check for port number
  pinMode(sensorPin, INPUT_PULLDOWN);
  //client.setCallback(callback);/Initiates callback if there is a message coming in from a topic

}

void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* message, unsigned int length) {//This callback is to respond to messages coming in from a subscribed topic.
  //Serial.print("Message arrived on topic: ");
  //Serial.print(topic);
  //Serial.print(". Message: ");
  //String messageTemp;
  
  //for (int i = 0; i < length; i++) {
    //Serial.print((char)message[i]);
    //messageTemp += (char)message[i];
  //}
  //Serial.println();

  // Feel free to add more if statements to control more GPIOs with MQTT

  // If a message is received on the topic esp32/output, you check if the message is either "on" or "off". 
  // Changes the output state according to the message
  //if (String(topic) == "esp32/output") {
    //Serial.print("Changing output to ");
    //if(messageTemp == "on"){
      //Serial.println("on");
      //digitalWrite(ledPin, HIGH);
    //}
    //else if(messageTemp == "off"){
      //Serial.println("off");
      //digitalWrite(ledPin, LOW);
    //}
  //}
}

void reconnect() {
  // Loop until reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("ESP8266Client")) {
      Serial.println("connected");
      // Subscribe
      // client.subscribe("esp32/output");// Put the topic to subscribe to, but we don't need to.
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 1 second");
      // Wait 1 second before retrying
      delay(1000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  Serial.print("Reading...");
  bool val = digitalRead(17);
  Serial.println(val);
  if (val == HIGH) {
    //lastMsg = now;
    
    // Convert the value to a char array
    //char tempString[8];
    //dtostrf(temperature, 1, 2, tempString);
    //Serial.print("Temperature: ");
    //Serial.println(tempString);
    //client.publish("esp32/temperature", tempString);

    //humidity = bme.readHumidity();
    
    // Convert the value to a char array
    //char humString[8];
    //dtostrf(humidity, 1, 2, humString);
    //Serial.print("Humidity: ");
    //Serial.println(humString);
    //client.publish("esp32/humidity", humString);
    
    String presenceString = "1";
    int str_len = presenceString.length() + 1;
    char char_array[str_len];
    presenceString.toCharArray(char_array, str_len);
    client.publish("esp32/homeID/RoomID", char_array);
    Serial.println("Published!");
    val = LOW;
    Serial.println(val);
    delay(5000);
  }
}
