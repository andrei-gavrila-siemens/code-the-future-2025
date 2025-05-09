/*
  takethesponge.ino

 This example commands to the Braccio to take a sponge from the table and it shows to the user

 Created on 18 Nov 2015
 by Andrea Martino

 This example is in the public domain.
*/

#include <Braccio.h>
#include <Servo.h>


Servo base;
Servo shoulder;
Servo elbow;
Servo wrist_rot;
Servo wrist_ver;
Servo gripper;


void setup() {  
  //Initialization functions and set up the initial position for Braccio
  //All the servo motors will be positioned in the "safety" position:
  //Base (M1):90 degrees
  //Shoulder (M2): 45 degrees
  //Elbow (M3): 180 degrees
  //Wrist vertical (M4): 180 degrees
  //Wrist rotation (M5): 90 degrees
  //gripper (M6): 10 degrees
  Braccio.begin();

   Braccio.ServoMovement(20, 0, 90, 90, 90, 90, 10);

  delay(1000); // Optional: wait 1 second before starting loop
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

  //Starting position
                      //(step delay  M1 , M2 , M3 , M4 , M5 , M6);
 Braccio.ServoMovement(20,         0  ,  90, 180, 180,  0, 10);
 Braccio.ServoMovement(20,         0  ,  90, 180, 180,  0, 70);
 Braccio.ServoMovement(20,         20  ,  90, 180, 180,  0,  70);
 Braccio.ServoMovement(20,         40  ,  90, 180, 180,  0,  70);
 Braccio.ServoMovement(20,         60  ,  90, 180, 180,  0,  70);
 Braccio.ServoMovement(20,         80  ,  90, 180, 180,  0,  70);
 Braccio.ServoMovement(20,         100  ,  90, 180, 180,  0,  70);
 Braccio.ServoMovement(20,         120  ,  90, 180, 180,  0,  70);
 Braccio.ServoMovement(20,         140  ,  90, 180, 180,  0,  70);
 Braccio.ServoMovement(20,         160  ,  90, 180, 180,  0,  70);
 Braccio.ServoMovement(20,         180  ,  90, 180, 180,  0,  70);
  Braccio.ServoMovement(20,         180  ,  90, 180, 190,  0,  10);
  Braccio.ServoMovement(20,         180  ,  90, 180, 190,  0,  10);
 
 




}
