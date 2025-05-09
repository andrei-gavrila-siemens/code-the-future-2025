#include <Braccio.h>
#include <Servo.h>

const uint8_t trigPin = 30;
const uint8_t echoPin = 32;

int distance;

Servo base;
Servo shoulder;
Servo elbow;
Servo wrist_ver;
Servo wrist_rot;
Servo gripper;

void setup() {
  Braccio.begin();pinMode(trigPin, OUTPUT);
  digitalWrite(trigPin, LOW);
  pinMode(echoPin, INPUT);
  Serial.begin(9600);
}

int getDistanceCM() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH);
  distance = duration * 0.034 / 2;
  return distance;
}

int scanForBottle() {
  for (int baseAngle = 0; baseAngle <= 150; baseAngle += 2) {
    Braccio.ServoMovement(20, baseAngle, 140, 165, 50, 90, 10);
    delay(300);
    int distance = getDistanceCM();
    if (distance < 6 && !(baseAngle > 95 && baseAngle < 105)) {
      Serial.print(baseAngle);
      return baseAngle;
    }
  }
  return -1; // Not found
}

void loop() {

  int detectedAngle = scanForBottle();
  if (detectedAngle != -1) {

    Braccio.ServoMovement(20, detectedAngle, 140, 165, 50, 90, 10); // starting pos
    delay(1000);
    Braccio.ServoMovement(20, detectedAngle, 140, 175, 50, 90, 10); // move to bottle
    Braccio.ServoMovement(10, detectedAngle, 140, 175, 50, 90, 73); // close grip
    Braccio.ServoMovement(20, detectedAngle, 140, 145, 30, 90, 73); // lift

    // Move to plant
    Braccio.ServoMovement(20, 150, 140, 145, 30, 90, 73); // plant position
    Braccio.ServoMovement(20, 150, 140, 145, 30, 15, 73); // pour
    delay(1000); // simulate watering

    // Return bottle
    Braccio.ServoMovement(20, 150, 140, 145, 30, 90, 73); // straighten
    Braccio.ServoMovement(20, detectedAngle, 140, 145, 30, 90, 73); // return
    Braccio.ServoMovement(10, detectedAngle, 140, 175, 50, 90, 73); //get down
    Braccio.ServoMovement(20, detectedAngle,  140, 175, 50, 90, 10); // open gripper

    // Idle pose
    Braccio.ServoMovement(20, 90, 90, 90, 90, 90, 10); // idle
    delay(5000);
  }
}
