#include <Braccio.h>
#include <Servo.h>

Servo base;
Servo shoulder;
Servo elbow;
Servo wrist_rot;
Servo wrist_ver;
Servo gripper;

void setup() {
  Braccio.begin();
  delay(200);
  ridicare(2);
}

void loop() {
  // nimic
}

void ridicare(int nr){

  for(int i=0; i<nr; i++){
    Braccio.ServoMovement(20, 120, 75, 80, 40, 90, 10);
    delay(400);

    // merge pe pozitia cubului
    Braccio.ServoMovement(20, 138, 75, 75, 40, 90, 10);
    delay(500);

    // se apleaca
    Braccio.ServoMovement(20, 138, 65, 65, 40, 90, 10);
    delay(800);

    // prinde
    Braccio.ServoMovement(20, 134, 55, 65, 40, 90, 70);
    delay(500);

    // ridica
    Braccio.ServoMovement(20, 134, 55, 90, 50, 90, 70);
    delay(400);

    // duce spre stânga
    Braccio.ServoMovement(20, 174, 55, 90, 50, 90, 70);
    delay(400);

    // poziție de lăsare
    Braccio.ServoMovement(20, 174, 55, 65, 50, 90, 70);
    delay(400);

    // deschide gripper
    Braccio.ServoMovement(20, 174, 55, 65, 50, 90, 10);
    delay(500);
  }
}