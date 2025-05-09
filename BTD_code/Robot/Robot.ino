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

bool isIdle = false;
int previousMillis = 0;
int baseAngle_idle = 0;
int shoulderAngle_idle = 0;
int elbowAngle_idle = 180;
int wristVerAngle_idle = 90;
int wristRotAngle_idle = 90;
int gripperAngle_idle = 73;

int baseAngle_auto_start = 0;
int shoulderAngle_auto_start = 0;
int elbowAngle_auto_start = 180;
int wristVerAngle_auto_start = 90;
int wristRotAngle_auto_start = 90;
int gripperAngle_auto_start = 73;

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
  idle();
}

void loop() 
{
  joystickConfig(X, Y);

  if (fBtnValue)
  {

  }

  if (aBtnValue) 
  {
    long currentMillis = millis();
    if (currentMillis - previousMillis > idleTimer)
    {
      isIdle = true;
      idle();
      Serial.println("Idle called");
      previousMillis = currentMillis;
    }
  }

  if (isIdle)
  {
    idle();
    isIdle = false;
  }
  else
  {
    armController(); 
    Braccio.ServoMovement((110-sqrt(pow(xAxisValue, 2))), baseAngle_idle, shoulderAngle_idle, elbowAngle_idle, wristVerAngle_idle, wristRotAngle_idle, gripperAngle_idle);
  }
}

void armController()
{   
  baseAngle_idle += xAxisValue * .1;
  baseAngle_idle = constrain(baseAngle_idle, 0, 180);
  shoulderAngle_idle += yAxisValue * .1;
  if (shoulderAngle_idle < 160)
  {
    wristVerAngle_idle = 192 - shoulderAngle_idle;
    wristVerAngle_idle = constrain(wristVerAngle_idle, 0, 180);
  }

  shoulderAngle_idle = constrain(shoulderAngle_idle, 0, 180);
  
  if (dBtnValue) 
  {
    gripperAngle_idle = 10;
  }

  if (bBtnValue) 
  {
    gripperAngle_idle = 73;
  }
}

void joystickConfig(int xAxis, int yAxis)
{
  xAxisValue = analogRead(xAxis);
  yAxisValue = analogRead(yAxis);
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
}

// Normalize joystick values to -1 to 1 range
int mapToRange(int value) 
{
  return (int)((float)(value - JOYSTICK_CENTER) / (JOYSTICK_CENTER) * 100);
}

void idle()
{
  baseAngle_idle = 0;
  shoulderAngle_idle = 0;
  elbowAngle_idle = 180;
  wristVerAngle_idle = 180;
  wristRotAngle_idle = 90;
  gripperAngle_idle = 73;

  Braccio.ServoMovement(60, 0, 0, 180, 180, 90, 73);
}