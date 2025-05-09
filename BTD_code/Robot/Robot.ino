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
#include <JoystickShield.h>

Servo base;
Servo shoulder;
Servo elbow;
Servo wrist_rot;
Servo wrist_ver;
Servo gripper;

const int GripPressed = 2;
const int xAxisMovement = 0;
const int yAxisMovement = 1;

#define A 5

const int JOYSTICK_MIN = 0;
const int JOYSTICK_MAX = 4095;
const int JOYSTICK_CENTER = 2047;
const int JOYSTICK_DEADZONE = 200;

int baseAngle = 90;
int shoulderAngle = 90;
int elbowAngle = 90;
int wristVerAngle = 90;
int wristRotAngle = 90;
int gripperAngle = 73;

JoystickShield joystickShield;

bool isGrabbing = false;
bool isJoystickBtnPressed = false;

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


  joystickShield.calibrateJoystick();

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
  joystickShield.processEvents();

  //joystickInputs(GripPressed);
  armController(); 

  Braccio.ServoMovement(50, baseAngle, shoulderAngle, elbowAngle, wristVerAngle, wristRotAngle, gripperAngle);

  //Wait 1 second
  delay(50);
}

void armController()
{   
    if (joystickShield.isRight()) {
      baseAngle += 5;
      Serial.println("Right");
    }   
    if (joystickShield.isLeft()) {
      baseAngle -= 5;
      Serial.println("Left");
    }
     if (joystickShield.isUp()) {
      shoulderAngle += 5;
      Serial.println("Up");
    } //move gripper
    if (joystickShield.isDown()) {
      shoulderAngle -= 5;
      Serial.println("Down");
    }
    if (joystickShield.isUpButton()) {
      elbowAngle += 5;
      Serial.println("Up clicked");
    }
    if (joystickShield.isDownButton()) {
      elbowAngle -= 5;
      Serial.println("Down clicked");
    }

    
    // if (joystickShield.isRightButton()) {
    //   elbowAngle += 5;
    //   Serial.println("Right clicked");
    // }
    // if (joystickShield.isLeftButton()) {
    //   elbowAngle -= 5;
    //   Serial.println("Left clicked");
    // }
    if (joystickShield.isJoystickButton()) 
    {
      if(!isJoystickBtnPressed)
      {
        if (isGrabbing)
        {
          isGrabbing = false;
          gripperAngle = 10;
          Serial.println("Gripper open");
        }
        else
        {
          isGrabbing = true;
          gripperAngle = 90;
          Serial.println("Gripper close");
        }

        isJoystickBtnPressed = true;
      }
    }
    else
    {
      isJoystickBtnPressed = false;
    }
}



