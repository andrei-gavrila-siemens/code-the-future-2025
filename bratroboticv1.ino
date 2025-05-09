#include <Braccio.h>
#include <Servo.h>

Servo base;
Servo shoulder;
Servo elbow;
Servo wrist_rot;
Servo wrist_ver;
Servo gripper;


const int joyX = A0; 
const int joyY = A1; 
const int buttonA = 2; 
const int buttonC = 3;

const int threshold = 100;

int baseAngle = 0;
int shoulderAngle = 90;
int elbowAngle = 90;

bool lastButtonAState = HIGH;

void setup() {
  pinMode(buttonA, INPUT_PULLUP);
  Braccio.begin();
  Braccio.ServoMovement(20, baseAngle, shoulderAngle, elbowAngle, 90, 180, 10);
  
}

void loop() {
  // Citim valorile joystickului
  int xVal = analogRead(joyX);
  int yVal = analogRead(joyY);

  if (xVal < 512 - threshold) {
    baseAngle -= 5;
  } else if (xVal > 512 + threshold) {
    baseAngle += 5;
  }

  if (yVal < 512 - threshold) {
    shoulderAngle -= 5;
  } else if (yVal > 512 + threshold) {
    shoulderAngle += 5;
  }


  bool currentButtonAState = digitalRead(buttonA);
  if (lastButtonAState == HIGH && currentButtonAState == LOW) {
    elbowAngle += 5;
    elbowAngle = constrain(elbowAngle, 0, 180);
  }
  lastButtonAState = currentButtonAState;
  

 
  baseAngle = constrain(baseAngle, 0, 180);
  shoulderAngle = constrain(shoulderAngle, 15, 165);

  
  Braccio.ServoMovement(10, baseAngle, shoulderAngle, elbowAngle, 90, 180, 10);

  
}

