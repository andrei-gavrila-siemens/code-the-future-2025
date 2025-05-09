/*
  simpleMovements.ino

 This  sketch simpleMovements shows how they move each servo motor of Braccio

 Created on 18 Nov 2015
 by Andrea Martino

 This example is in the public domain.
 */

#include <Braccio.h>
#include <Servo.h>
#include <Arduino.h>

Servo base;
Servo shoulder;
Servo elbow;
Servo wrist_rot;
Servo wrist_ver;
Servo gripper;

const int GripPressed = 2;
const int xAxisMovement = 0;
const int yAxisMovement = 1;

#define X A0
#define Y A1
#define A 8
#define B 2
#define C 4
#define D 7
#define E 0
#define F 1

const int JOYSTICK_MIN = 0;
const int JOYSTICK_MAX = 1024;
const int JOYSTICK_CENTER = 512;
const int JOYSTICK_DEADZONE = 10;

int baseAngle = 90;
int shoulderAngle = 90;
int elbowAngle = 90;
int wristVerAngle = 90;
int wristRotAngle = 90;
int gripperAngle = 73;

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
  //Initialization functions and set up the initial position for Braccio
  //All the servo motors will be positioned in the "safety" position:
  //Base (M1):90 degrees
  //Shoulder (M2): 45 degrees
  //Elbow (M3): 180 degrees
  //Wrist vertical (M4): 180 degrees
  //Wrist rotation (M5): 90 degrees
  //gripper (M6): 10 degrees
  Serial.begin(9600);

  pinMode(A, INPUT_PULLUP);
  pinMode(B, INPUT_PULLUP);
  pinMode(C, INPUT_PULLUP);
  pinMode(D, INPUT_PULLUP);
  pinMode(E, INPUT_PULLUP);
  pinMode(F, INPUT_PULLUP);

  delay(1000);
  
  Braccio.begin();
}

void loop() {
   /*
   Step Delay: a milliseconds delay between the movement of each servo.  Allowed values from 10 to 30 msec.
   M1=base degrees. Allowed values from 0 to 180 degrees
   M2=shoulder degrees. Allowed values from 15 to 165 degrees
   M3=elbow degrees. Allowed values from 0 to 180 degrees
   M4=wrist vertical degrees. Allowed values from 0 to 180 degrees
   M5=wrist rotation degrees. Allowed values from 0 to 180 degrees
   M6=gripper degrees. Allowed values from 10 to 73 degrees. 10: the toungue is open, 73: the gripper is closed.
  */
  
                       //(step delay, M1, M2, M3, M4, M5, M6);



  // Braccio.ServoMovement(10, baseAngle, shoulderAngle, elbowAngle, wristVerAngle, wristRotAngle, gripperAngle);
  // Braccio.ServoMovement(20,           0,  15, 180, 170, 0,  73);  

  //Wait 1 second
  joystickConfig(X, Y);
  armController(); 

  
  if(xValue != 0)
  {
    Braccio.ServoMovement(101 / (xValue+1) + 30, baseAngle, shoulderAngle, elbowAngle, wristVerAngle, wristRotAngle, gripperAngle);
  }
  else
  {
    Braccio.ServoMovement(50, baseAngle, shoulderAngle, elbowAngle, wristVerAngle, wristRotAngle, gripperAngle);
  }

  //Wait 1 second
  delay(25);
}

void armController()
{   
    baseAngle += xValue * .3f;

    // if (joystickShield.isRight()) {
    //   baseAngle += 5;
    //   Serial.println("Right");
    // }   
    // if (joystickShield.isLeft()) {
    //   baseAngle -= 5;
    //   Serial.println("Left");
    // }
    //  if (joystickShield.isUp()) {
    //   shoulderAngle += 5;
    //   Serial.println("Up");
    // } //move gripper
    // if (joystickShield.isDown()) {
    //   shoulderAngle -= 5;
    //   Serial.println("Down");
    // }
    // if (joystickShield.isUpButton()) {
    //   elbowAngle += 5;
    //   Serial.println("Up clicked");
    // }
    // if (joystickShield.isDownButton()) {
    //   elbowAngle -= 5;
    //   Serial.println("Down clicked");
    // }

    
    // if (joystickShield.isRightButton()) {
    //   elbowAngle += 5;
    //   Serial.println("Right clicked");
    // }
    // if (joystickShield.isLeftButton()) {
    //   elbowAngle -= 5;
    //   Serial.println("Left clicked");
    // }
    // if (joystickShield.isJoystickButton()) 
    // {
    //   if(!isJoystickBtnPressed)
    //   {
    //     if (isGrabbing)
    //     {
    //       isGrabbing = false;
    //       gripperAngle = 10;
    //       Serial.println("Gripper open");
    //     }
    //     else
    //     {
    //       isGrabbing = true;
    //       gripperAngle = 90;
    //       Serial.println("Gripper close");
    //     }

    //     isJoystickBtnPressed = true;
    //   }
    // }
    // else
    // {
    //   isJoystickBtnPressed = false;
    // }
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
  
  // intmappedX = mapJoystickValue(1024 - xValue);
  // intmappedY = mapJoystickValue(yValue);
  valueA = !digitalRead(A);
  valueB = !digitalRead(B);
  valueC = !digitalRead(C);
  valueD = !digitalRead(D);
  valueE = !digitalRead(E);
  valueF = !digitalRead(F);

  Serial.print("MOV: ");
  Serial.print(xValue);
  Serial.print(" ; ");
  Serial.print(yValue);
  Serial.print("- A: ");
  Serial.print(valueA);
  Serial.print("- B: ");
  Serial.print(valueB);
  Serial.print("- C: ");
  Serial.print(valueC);
  Serial.print("- D: ");
  Serial.print(valueD);
  Serial.print("- E: ");
  Serial.print(valueE);
  Serial.print("- F: ");
  Serial.println(valueF);
}

// Normalize joystick values to -1 to 1 range
int mapToRange(int value) {
    return (int)((float)(value - JOYSTICK_CENTER) / (JOYSTICK_CENTER) * 100);
}

// int mapJoystickValue(int value) {
//   // Map the joystick's 0-4095 range to -32768 to 32767
//   return map(value, JOYSTICK_MIN, JOYSTICK_MAX, 0, 180);
// }


