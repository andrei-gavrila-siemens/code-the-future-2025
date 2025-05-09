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

int baseAngle_idle = 0;
int shoulderAngle_idle = 0;
int elbowAngle_idle = 180;
int wristVerAngle_idle = 90;
int wristRotAngle_idle = 90;
int gripperAngle_idle = 73;

int baseAngle = 0;
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
  // Serial.println(state);

  switch (state)
  {
    default:
    case Idle:
      runIdle();
      Braccio.ServoMovement(60, baseAngle, shoulderAngle, elbowAngle, wristVerAngle, wristRotAngle, gripperAngle);
      break;
    case Auto:
      runAuto();
      Braccio.ServoMovement(60, baseAngle, shoulderAngle, elbowAngle, wristVerAngle, wristRotAngle, gripperAngle);
      break;
    case Manual:
      runManual();
      Braccio.ServoMovement((110-sqrt(pow(xAxisValue, 2))), baseAngle, shoulderAngle, elbowAngle, wristVerAngle, wristRotAngle, gripperAngle);
      break;
  }
}

void runIdle()
{
  // Serial.println("IDLE");

  baseAngle = 0;
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

  if (aBtnValue)
  {
    state = Idle;
  }
}

void runAuto()
{
  if (cBtnValue)
  {
    state = Manual;
  }
}

void armController()
{   
  baseAngle += xAxisValue * .1;
  baseAngle = constrain(baseAngle, 0, 180);
  shoulderAngle += yAxisValue * .1;
  if (shoulderAngle < 160)
  {
    wristVerAngle = 192 - shoulderAngle;
    wristVerAngle = constrain(wristVerAngle, 0, 180);
  }

  shoulderAngle = constrain(shoulderAngle, 0, 180);
  
  if (dBtnValue) 
  {
    gripperAngle = 10;
  }

  if (bBtnValue) 
  {
    gripperAngle = 73;
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