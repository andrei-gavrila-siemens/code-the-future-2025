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

bool isGrabbing = false;
bool isJoystickBtnPressed = false;

int xValue;
int yValue;

int valueA;
int valueB;
int valueC;
int valueD;
int valueE;
int valueF;

void setup() {
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

void loop() {

  joystickConfig(X, Y);

  if (!digitalRead(A)) {

    long currentMillis = millis();
    if(currentMillis - previousMillis > idleTimer)
     {
       isIdle = true;
       idle();
       Serial.println("Idle called");
       previousMillis = currentMillis;

     }
    }

    if(isIdle)
    {
      idle();
      isIdle = false;
    }
    else
    {
      armController(); 
      Braccio.ServoMovement((110-sqrt(pow(xValue, 2))), baseAngle_idle, shoulderAngle_idle, elbowAngle_idle, wristVerAngle_idle, wristRotAngle_idle, gripperAngle_idle);
    }
}

void armController()
{   
  baseAngle_idle += xValue * .1;
  baseAngle_idle = constrain(baseAngle_idle, 0, 180);
  shoulderAngle_idle += yValue * .1;
  if (shoulderAngle_idle < 160)
  {
    wristVerAngle_idle = 192 - shoulderAngle_idle;
    wristVerAngle_idle = constrain(wristVerAngle_idle, 0, 180);
  }

  shoulderAngle_idle = constrain(shoulderAngle_idle, 0, 180);
  
  if (valueD) {
    gripperAngle_idle = 10;
    //Serial.println("Up clicked");
  }
  if (valueB) {
    gripperAngle_idle = 73;
    //Serial.println("Down clicked");
  }
}

void joystickConfig(int xAxis, int yAxis)
{
  xValue = analogRead(xAxis);
  yValue = analogRead(yAxis);
  xValue = mapToRange(xValue);
  yValue = mapToRange(yValue);

  if (xValue >= -5 && xValue <= 5)
  {
    xValue = 0;
  }

  if (yValue >= -5 && yValue <= 5)
  {
    yValue = 0;
  }

  valueA = !digitalRead(A);
  valueB = !digitalRead(B);
  valueC = !digitalRead(C);
  valueD = !digitalRead(D);
  valueE = !digitalRead(E);
  valueF = !digitalRead(F);

}

// Normalize joystick values to -1 to 1 range
int mapToRange(int value) {
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