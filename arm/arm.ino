#include <Braccio.h>
#include <Servo.h>

Servo base;
Servo shoulder;
Servo elbow;
Servo wrist_ver;
Servo wrist_rot;
Servo gripper;

void setup()
{
  Braccio.begin();
}

void loop()
{
  Braccio.ServoMovement(20, 0, 135, 180, 70, 90, 10); //starting pos
  delay(1000);
  Braccio.ServoMovement(20, 0, 135, 180, 70, 90, 10); //moves to bottle
  Braccio.ServoMovement(10, 0, 135, 180, 70, 90, 73);//close tongues
  Braccio.ServoMovement(20, 0, 135, 150, 50, 90, 73);//bring up
  Braccio.ServoMovement(20, 0, 135, 150, 50, 15, 73); //incline
  Braccio.ServoMovement(20, 0, 135, 150, 50, 90, 73); //straight pos before putting it down
  Braccio.ServoMovement(20, 0, 135, 180, 70, 90, 73); //start pos
  Braccio.ServoMovement(20, 0, 135, 180, 70, 90, 10); //open grip
  Braccio.ServoMovement(20, 0, 90, 90, 90, 90, 10); //goes straight till the next time it needs to water the plant
  delay(5000);
}