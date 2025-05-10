
#include <Braccio.h>
#include <Servo.h>

Servo base;
Servo shoulder;
Servo elbow;
Servo wrist_rot;
Servo wrist_ver;
Servo gripper;

int level = 0;
bool started = false;
bool action = false;

void setup() {
  //Initialization functions and set up the initial position for Braccio
  //All the servo motors will be positioned in the "safety" position:
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

  action = !action;
  if(action)
    addBlock();
  else
    thrashBlock();

  // int input = Serial.parseInt();  // Read the number

  // // Clear any remaining characters in the serial buffer
  // while (Serial.available() > 0) {
  //   Serial.read();
  // }

  // // Convert to boolean (0 = false, any other number = true)
  // switch (input) {
  //   case 0:
  //     delay(500);
  //     break;
  //   case 1:
  //     thrashBlock();
  //     break;
  //   case 2:
  //     addBlock();
  //     break;
  // }
}

void thrashBlock() {
  if (!started) {
    // rotate
    Braccio.ServoMovement(20, 180, 90, 90, 90, 90, 10);
    delay(1000);
    started = true;
  }

  // get down
  Braccio.ServoMovement(20, 130, 130 - level * 6, 180, 40, 0, 10);
  delay(1000);
  // move to block and pick it up
  Braccio.ServoMovement(20, 90, 130, 180, 40, 0, 70);
  delay(1000);
  Braccio.ServoMovement(10, 90, 143, 180, 40, 0, 70);
  delay(1000);
  Braccio.ServoMovement(5, 50, 143, 180, 40, 0, 70);
  delay(1000);
  // go away from placement
  Braccio.ServoMovement(20, 130, 130, 180, 40, 0, 70);
  delay(1000);
  Braccio.ServoMovement(20, 130, 100, 180, 40, 0, 70);
  delay(1000);

  // let block down and move up
}

void addBlock() {
  if (!started) {
    // rotate
    Braccio.ServoMovement(20, 180, 90, 90, 90, 90, 10);
    delay(1000);
    started = true;
  }

  // get down
  Braccio.ServoMovement(20, 130, 130 - level * 6, 180, 40, 0, 10);
  delay(1000);
  // move to block and pick it up
  Braccio.ServoMovement(20, 75, 130, 180, 40, 0, 10);
  delay(1000);
  Braccio.ServoMovement(10, 75, 143, 180, 40, 0, 70);
  delay(1000);
  Braccio.ServoMovement(20, 75, 130, 180, 40, 0, 70);
  delay(1000);
  // go away from placement
  Braccio.ServoMovement(20, 130, 130, 180, 40, 0, 70);
  delay(1000);
  Braccio.ServoMovement(20, 130, 100, 180, 40, 0, 70);
  delay(1000);

  // let block down and move up
  Braccio.ServoMovement(20, 180, 100, 180, 40, 0, 70);
  delay(1000);
  Braccio.ServoMovement(20, 180, 143 - level * 6, 180, 40, 0, 70);
  delay(1000);
  Braccio.ServoMovement(20, 180, 143 - level * 6, 180, 40, 0, 10);
  delay(1000);
  Braccio.ServoMovement(20, 180, 130 - level * 6, 180, 40, 0, 10);
  delay(1000);

  level++;
  level = level >= 5 ? 0 : level;
}
