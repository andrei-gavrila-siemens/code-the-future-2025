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
const int buttonB = 4;
const int buttonC = 13;
const int buttonD = 8;
const int buttonE = 7;

const int threshold = 100;

int baseAngle = 0;
int shoulderAngle = 90;
int elbowAngle = 90;
int wrist_rotAngle = 90;
int gripperAngle = 10;

bool lastButtonEState = HIGH;
bool gripperState = false;

void setup() {
  pinMode(buttonA, INPUT_PULLUP);
  pinMode(buttonB, INPUT_PULLUP);
  pinMode(buttonC, INPUT_PULLUP);
  pinMode(buttonD, INPUT_PULLUP);
  pinMode(buttonE, INPUT_PULLUP);

  Braccio.begin();
  Braccio.ServoMovement(20, baseAngle, shoulderAngle, elbowAngle, wrist_rotAngle, 180, gripperAngle);
}

void loop() {
  int xVal = analogRead(joyX);
  int yVal = analogRead(joyY);

  if (xVal < 512 - threshold) {
    baseAngle -= 2;
  } else if (xVal > 512 + threshold) {
    baseAngle += 2;
  }

  if (yVal < 512 - threshold) {
    shoulderAngle -= 1;
  } else if (yVal > 512 + threshold) {
    shoulderAngle += 1;
  }

  if (digitalRead(buttonA) == LOW) {
    elbowAngle += 2;
    elbowAngle = constrain(elbowAngle, 0, 180);
  }

  if (digitalRead(buttonB) == LOW) {
    elbowAngle -= 2;
    elbowAngle = constrain(elbowAngle, 0, 180);
  }

  if (digitalRead(buttonC) == LOW) {
    wrist_rotAngle -= 2;
    wrist_rotAngle = constrain(wrist_rotAngle, 0, 180);
  }

  if (digitalRead(buttonD) == LOW) {
    wrist_rotAngle += 2;
    wrist_rotAngle = constrain(wrist_rotAngle, 0, 180);
  }

  
  bool currentButtonEState = digitalRead(buttonE);
  if (lastButtonEState == HIGH && currentButtonEState == LOW) {
    gripperState = !gripperState;
  }
  lastButtonEState = currentButtonEState;

  gripperAngle = gripperState ? 70 : 10;

  baseAngle = constrain(baseAngle, 0, 180);
  shoulderAngle = constrain(shoulderAngle, 15, 165);

  Braccio.ServoMovement(10, baseAngle, shoulderAngle, elbowAngle, wrist_rotAngle, 180, gripperAngle);

  delay(20);  
}

