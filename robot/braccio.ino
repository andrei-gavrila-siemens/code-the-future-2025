#include <Braccio.h>
#include <Servo.h>

// Servo-urile individuale
Servo base;
Servo shoulder;
Servo elbow;
Servo wrist_rot;
Servo wrist_ver;
Servo gripper;

void ridicare()

void setup() {
   
   Braccio.begin();

  delay(200);

    // merge in laterala stanga aproape pe pozitia cubului
   Braccio.ServoMovement(20,    120,75,80,40,90,10);
    delay(400);
    // merge pe pozitia cubului
    Braccio.ServoMovement(20,    138,75,75,40,90,10);

  delay(500);
  // se apleaca pe pozitia cubului
  Braccio.ServoMovement(20,    138,65,65,40,90,10);
  delay(800);

  // prinde cubul
  Braccio.ServoMovement(20,    134,55,65,40,90,70);

  delay(500);

  //ridica cubul
  Braccio.ServoMovement(20,    134,55,90,50,90,70);

}

void loop() {
  // nimic
}
