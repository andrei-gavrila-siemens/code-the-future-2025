
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
    Braccio.ServoMovement(20, baseAngle, 135, 170, 120, 90, 10);
    delay(300);
    int distance = getDistanceCM();
    if (distance <6 && !(baseAngle > 95 && baseAngle < 105)) {
      return baseAngle + 5;  // Adjust the angle for proper placement
    }
  }
  return -1;  // Not found
}

void loop() {
  int plantAngle=0;
  int detectedAngle = scanForBottle();
  if (detectedAngle != -1) {
    // Move to bottle position
    Braccio.ServoMovement(20, detectedAngle, 135, 170, 120, 90, 10); 
    delay(1000);
    Braccio.ServoMovement(20, detectedAngle, 145, 165, 130, 90, 10); // Move to bottle
    Braccio.ServoMovement(20, detectedAngle, 145, 165, 130, 90, 73); // Close gripper
    //Braccio.ServoMovement(20, detectedAngle, 90, 130, 120, 90, 73); // Lift bottle
    //Braccio.ServoMovement(10, detectedAngle, 90, 150, 120, 90, 73);

    // Move to plant and simulate watering
    
    Braccio.ServoMovement(40, plantAngle, 80, 160, 0, 0, 73); 
    Braccio.ServoMovement(40, plantAngle, 80, 160, 0, 45, 73); 
    delay(1000);
    Braccio.ServoMovement(40, 0, 80, 160, 0, 0, 73); 
    
    Braccio.ServoMovement(20, detectedAngle, 150, 90, 90, 0, 73);
    Braccio.ServoMovement(40, detectedAngle, 145, 165, 115, 90, 73);
    Braccio.ServoMovement(20, detectedAngle, 145, 165, 115, 90, 10); // Open gripper

    // Return to idle pose
    Braccio.ServoMovement(20, detectedAngle, 150, 90, 90, 90, 10); // Idle position
    delay(5000);
  }
}
