#include <WiFiS3.h>
#include <PubSubClient.h>

#define UART_BAUDRATE 9600

// WiFi credentials
const char* ssid = "Guest-WiFi";
const char* password = "icdt2020";

// MQTT Broker details
const char* mqtt_server = "172.31.99.35";
const int mqtt_port = 1884;
const char* mqtt_topic = "esp32/distance";  // Topic to publish
const char* subscribe_topic = "rpi5/data";  // Topic to subscribe to

WiFiClient wifiClient;
PubSubClient client(wifiClient);

// Ultrasonic sensor pins
#define TRIG_PIN 9
#define ECHO_PIN 10

// WiFi and MQTT setup
void setup_wifi() {
  Serial.print("Connecting to ");
  Serial.println(ssid);

  while (WiFi.begin(ssid, password) != WL_CONNECTED) {
    Serial.print(".");
    delay(1000);
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ArduinoUnoR4WiFiClient")) {
      Serial.println("connected");
      // Subscribe to the topic when connected
      client.subscribe(subscribe_topic);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 2 seconds");
      delay(2000);
    }
  }
}

// Callback function that gets called when a message arrives
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  
  // Convert payload to string and print
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println(message);  // Print the received message
  Serial1.println(message);  // TSend message trough UART to ATMEGA2560
  Serial.println("Sent to Mega: " + message);  // Message for debug
}

// Read distance from ultrasonic sensor
float readDistance() {
  long duration;
  float distance;

  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  duration = pulseIn(ECHO_PIN, HIGH);
  distance = duration * 0.034 / 2;

  return distance;
}

void setup() {
  Serial.begin(9600);      // Serial for print to monitor
  while (!Serial);

  // Setup pins for ultrasonic sensor
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // Setup WiFi + MQTT
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);  // Set callback function for incoming messages

  Serial1.begin(UART_BAUDRATE);  // Serial for sending data trough atmega2560
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();  // Keeps the connection alive and checks for new messages

  // Read distance
  float distance = readDistance();

  // Read internal CPU temperature (Uno R4 method)
  unsigned int raw = analogRead(20);
  float voltage = raw * (3.3 / 1023.0);
  float temperature = (voltage - 0.275) * 112.0;

  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.print(" cm, CPU Temp: ");
  Serial.print(temperature);
  Serial.println(" °C");

  // Create JSON message
  char buffer[150];
  sprintf(buffer, "{\"distance\": %.2f, \"cpu_temp\": %.2f}", distance, temperature);
  client.publish(mqtt_topic, buffer);
  Serial.print("Published JSON: ");
  Serial.println(buffer);

  delay(1000);  // Wait 1 second
}
