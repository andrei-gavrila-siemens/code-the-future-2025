#include <Braccio.h>
#include <Servo.h>

const uint8_t trigPin = 30;
const uint8_t echoPin = 32;

long duration;
int distance;

Servo base;
Servo shoulder;
Servo elbow;
Servo wrist_ver;
Servo wrist_rot;
Servo gripper;

void setup() {
  Braccio.begin();
  pinMode(trigPin, OUTPUT);
  digitalWrite(trigPin, LOW);
  pinMode(echoPin, INPUT);
  Serial.begin(9600);  // Set up serial communication at 9600 baud
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
  for (int baseAngle = 0; baseAngle <= 170; baseAngle += 2) {
    Braccio.ServoMovement(20, baseAngle, 90, 150, 120, 90, 10);
    delay(300);
    int distance = getDistanceCM();
    if (distance < 6 && !(baseAngle > 95 && baseAngle < 105)) {
      return baseAngle + 2;  // Adjust the angle for proper placement
    }
  }
  return -1;  // Not found
}

void waterPlant() {
  int detectedAngle = scanForBottle();
  if (detectedAngle != -1) {
    // Move to bottle position
    Braccio.ServoMovement(20, detectedAngle, 90, 150, 120, 90, 10); 
    delay(1000);
    Braccio.ServoMovement(20, detectedAngle, 90, 180, 120, 90, 10); // Move to bottle
    Braccio.ServoMovement(20, detectedAngle, 90, 180, 120, 90, 73); // Close gripper
    Braccio.ServoMovement(20, detectedAngle, 90, 130, 120, 90, 73); // Lift bottle
    Braccio.ServoMovement(10, detectedAngle, 90, 150, 120, 90, 73);

    // Move to plant and simulate watering
    Braccio.ServoMovement(20, 0, 45, 160, 0, 0, 73); 
    //Braccio.ServoMovement(20, 150, 100, 130, 90, 90, 73); // Move to plant
    //Braccio.ServoMovement(20, 150, 100, 130, 90, 0, 73);  // Pour water
    delay(1000);  // Simulate watering action

    // Return bottle to original position
    Braccio.ServoMovement(10, detectedAngle, 90, 150, 120, 90, 73);
    Braccio.ServoMovement(20, detectedAngle, 90, 130, 120, 90, 73); 
    Braccio.ServoMovement(20, detectedAngle, 90, 130, 120, 90, 10); // Open gripper

    // Return to idle pose
    Braccio.ServoMovement(20, detectedAngle, 90, 90, 90, 90, 10); // Idle position
    delay(5000);
  }
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readString();  // Read the incoming command from Raspberry Pi
    command.trim();  // Remove any extra spaces or newline characters

    if (command == "WATER") {
      waterPlant();  // Execute watering process when the command "WATER" is received
  }
}
}