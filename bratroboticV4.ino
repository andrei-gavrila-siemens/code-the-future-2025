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

bool lastButtonAState = HIGH;
bool lastButtonBState = HIGH;
bool lastButtonCState = HIGH;
bool lastButtonDState = HIGH;
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

  bool currentButtonBState = digitalRead(buttonB);
  if (lastButtonBState == HIGH && currentButtonBState == LOW) {
    elbowAngle -= 5;
    elbowAngle = constrain(elbowAngle, 0, 180);
  }
  lastButtonBState = currentButtonBState;

  bool currentButtonCState = digitalRead(buttonC);
  if (lastButtonCState == HIGH && currentButtonCState == LOW) {
    wrist_rotAngle -= 5;
    wrist_rotAngle = constrain(wrist_rotAngle, 0, 180);
  }
  lastButtonCState = currentButtonCState;

  bool currentButtonDState = digitalRead(buttonD);
  if (lastButtonDState == HIGH && currentButtonDState == LOW) {
    wrist_rotAngle += 5;
    wrist_rotAngle = constrain(wrist_rotAngle, 0, 180);
  }
  lastButtonDState = currentButtonDState;

  bool currentButtonEState = digitalRead(buttonE);
  if (lastButtonEState == HIGH && currentButtonEState == LOW) {
    gripperState = !gripperState;  
  }
  lastButtonEState = currentButtonEState;

  gripperAngle = gripperState ? 70 : 10;

  baseAngle = constrain(baseAngle, 0, 180);
  shoulderAngle = constrain(shoulderAngle, 15, 165);

  Braccio.ServoMovement(10, baseAngle, shoulderAngle, elbowAngle, wrist_rotAngle, 180, gripperAngle);
}

