#include <WiFiS3.h>
#include <PubSubClient.h>

const char* ssid = "Wannacryptic";
const char* password = "***********";

const char* mqtt_server = "192.168.43.236";
const int mqtt_port = 1884;
const char* mqtt_topic = "esp32/distance";

WiFiClient wifiClient;
PubSubClient client(wifiClient);

// Ultrasonic sensor pins
#define TRIG_PIN 9
#define ECHO_PIN 10

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
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 2 seconds");
      delay(2000);
    }
  }
}

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
  Serial.begin(9600);
  while (!Serial);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Read distance
  float distance = readDistance();
  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  // Convert distance to string and publish
  char payload[10];
  dtostrf(distance, 1, 2, payload);
  client.publish(mqtt_topic, payload);
  Serial.print("Published distance: ");
  Serial.println(payload);

  delay(1000);
}