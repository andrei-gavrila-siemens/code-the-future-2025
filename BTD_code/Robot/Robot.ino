#include <Braccio.h>
#include <Servo.h>
#include <Arduino.h>

#define X A0
#define Y A1
#define A 8
#define B 2
#define C 4
#define D 7
#define E 0
#define F 1
#define idleTimer 2000
#define JOYSTICK_CENTER 512

Servo base;
Servo shoulder;
Servo elbow;
Servo wrist_rot;
Servo wrist_ver;
Servo gripper;

int baseAngle_idle = 90;
int shoulderAngle_idle = 0;
int elbowAngle_idle = 180;
int wristVerAngle_idle = 90;
int wristRotAngle_idle = 90;
int gripperAngle_idle = 73;

int baseAngle_auto_start = 90;
int shoulderAngle_auto_start = 0;
int elbowAngle_auto_start = 180;
int wristVerAngle_auto_start = 90;
int wristRotAngle_auto_start = 90;

int baseAngle_auto_end = 90;
int shoulderAngle_auto_end = 0;
int elbowAngle_auto_end = 180;
int wristVerAngle_auto_end = 90;
int wristRotAngle_auto_end = 90;

int baseAngle = 90;
int shoulderAngle = 0;
int elbowAngle = 180;
int wristVerAngle = 90;
int wristRotAngle = 90;
int gripperAngle = 73;

bool isGrabbing = false;
bool isJoystickBtnPressed = false;

int xAxisValue;
int yAxisValue;

int aBtnValue;
int bBtnValue;
int cBtnValue;
int dBtnValue;
int eBtnValue;
int fBtnValue;

enum State {
  Idle,
  Auto,
  Manual
};

State state = Idle;

void setup() 
{
  Serial.begin(9600);

  pinMode(A, INPUT_PULLUP);
  pinMode(B, INPUT_PULLUP);
  pinMode(C, INPUT_PULLUP);
  pinMode(D, INPUT_PULLUP);
  pinMode(E, INPUT_PULLUP);
  pinMode(F, INPUT_PULLUP);

  Braccio.begin();
  state = Idle;
  // idle();
}

void loop()
{
  joystickConfig();
// Serial.print("xAxisValue: ");
// Serial.print(xAxisValue);
// Serial.print(" | yAxisValue: ");
// Serial.print(yAxisValue);
// Serial.print(" | aBtnValue: ");
// Serial.print(aBtnValue);
// Serial.print(" | bBtnValue: ");
// Serial.print(bBtnValue);
// Serial.print(" | cBtnValue: ");
// Serial.print(cBtnValue);
// Serial.print(" | dBtnValue: ");
// Serial.print(dBtnValue);
// Serial.print(" | eBtnValue: ");
// Serial.print(eBtnValue);
// Serial.print(" | fBtnValue: ");
// Serial.println(fBtnValue);


  switch (state)
  {
    default:
    case Idle:
      runIdle();
      Braccio.ServoMovement(60, baseAngle, shoulderAngle, elbowAngle, wristVerAngle, wristRotAngle, gripperAngle);
      break;
    case Auto:
      runAuto();
      break;
    case Manual:
      runManual();
      Braccio.ServoMovement((110-sqrt(pow(xAxisValue, 2))), baseAngle, shoulderAngle, elbowAngle, wristVerAngle, wristRotAngle, gripperAngle);
      break;
  }

  if (shoulderAngle < 160)
  {
    wristVerAngle = 192 - shoulderAngle;
    wristVerAngle = constrain(wristVerAngle, 0, 180);
  }

  shoulderAngle = constrain(shoulderAngle, 0, 180);
}

void runIdle()
{
  // Serial.println("IDLE");

  baseAngle = 90;
  shoulderAngle = 0;
  elbowAngle = 180;
  wristVerAngle = 180;
  wristRotAngle = 90;
  gripperAngle = 73;

  if (isAnyBtnPressed() && !aBtnValue)
  {
    state = Manual;
  }
}

void runManual()
{
  // Serial.println("RUN");
  armController();

  if (eBtnValue)
  {
    Serial.println("SAVED START");
    baseAngle_auto_start = baseAngle;
    shoulderAngle_auto_start = shoulderAngle;
    elbowAngle_auto_start = elbowAngle;
    wristVerAngle_auto_start = wristVerAngle;
    wristRotAngle_auto_start = wristRotAngle;
  }

  if (fBtnValue)
  {
    Serial.println("SAVED END");
    baseAngle_auto_end = baseAngle;
    shoulderAngle_auto_end = shoulderAngle;
    elbowAngle_auto_end = elbowAngle;
    wristVerAngle_auto_end = wristVerAngle;
    wristRotAngle_auto_end = wristRotAngle;
  }

  if (aBtnValue)
  {
    state = Idle;
  }

  if (cBtnValue)
  {
    state = Auto;
    cBtnValue = 0;
  }
}

void runAuto()
{
  baseAngle = baseAngle_auto_start;
  shoulderAngle = shoulderAngle_auto_start;
  elbowAngle = elbowAngle_auto_start;
  wristVerAngle = wristVerAngle_auto_start;
  wristRotAngle = wristRotAngle_auto_start;
  Braccio.ServoMovement(60, baseAngle, shoulderAngle, elbowAngle - 20, wristVerAngle, wristRotAngle, 10);

  joystickConfig();
  if (isAnyBtnPressed() && !cBtnValue)
  {
    state = Manual;
  }

  Braccio.ServoMovement(20, baseAngle, shoulderAngle, elbowAngle, wristVerAngle, wristRotAngle, 73);
  
  joystickConfig();
  if (isAnyBtnPressed() && !cBtnValue)
  {
    state = Manual;
  }

  baseAngle = baseAngle_auto_end;
  shoulderAngle = shoulderAngle_auto_end;
  elbowAngle = elbowAngle_auto_end;
  wristVerAngle = wristVerAngle_auto_end;
  wristRotAngle = wristRotAngle_auto_end;
  Braccio.ServoMovement(60, baseAngle, shoulderAngle, elbowAngle - 10, wristVerAngle, wristRotAngle, 73);

  joystickConfig();
  if (isAnyBtnPressed() && !cBtnValue)
  {
    state = Manual;
  }

  Braccio.ServoMovement(60, baseAngle, shoulderAngle, elbowAngle, wristVerAngle, wristRotAngle, 10);

  joystickConfig();
  if (isAnyBtnPressed() && !cBtnValue)
  {
    state = Manual;
  }
}

void armController()
{   
  baseAngle += xAxisValue * .1;
  baseAngle = constrain(baseAngle, 0, 180);
  shoulderAngle += yAxisValue * .1;
  
  if (dBtnValue) 
  {
    gripperAngle = 10;
    // open
  }

  if (bBtnValue) 
  {
    gripperAngle = 73;
    // closed
  }
}

bool isAnyBtnPressed()
{
  return (xAxisValue != 0 || yAxisValue != 0 || aBtnValue || bBtnValue || cBtnValue || dBtnValue || eBtnValue || fBtnValue);
}

void joystickConfig()
{
  xAxisValue = analogRead(X);
  yAxisValue = analogRead(Y);
  xAxisValue = mapToRange(xAxisValue);
  yAxisValue = mapToRange(yAxisValue);

  if (xAxisValue >= -5 && xAxisValue <= 5)
  {
    xAxisValue = 0;
  }

  if (yAxisValue >= -5 && yAxisValue <= 5)
  {
    yAxisValue = 0;
  }

  aBtnValue = !digitalRead(A);
  bBtnValue = !digitalRead(B);
  cBtnValue = !digitalRead(C);
  dBtnValue = !digitalRead(D);
  eBtnValue = !digitalRead(E);
  fBtnValue = !digitalRead(F);

// Serial.print("x: ");
// Serial.print(xAxisValue);
// Serial.print(" | y: ");
// Serial.print(yAxisValue);
// Serial.print(" | a: ");
// Serial.print(aBtnValue);
// Serial.print(" | b: ");
// Serial.print(bBtnValue);
// Serial.print(" | c: ");
// Serial.print(cBtnValue);
// Serial.print(" | d: ");
// Serial.print(dBtnValue);
// Serial.print(" | e: ");
// Serial.print(eBtnValue);
// Serial.print(" | f ");
// Serial.println(fBtnValue);
}

// Normalize joystick values to -1 to 1 range
int mapToRange(int value) 
{
  return (int)((float)(value - JOYSTICK_CENTER) / (JOYSTICK_CENTER) * 100);
}