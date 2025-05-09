#include <Braccio.h>
#include <Servo.h>

Servo base;
Servo shoulder;
Servo elbow;
Servo wrist_rot;
Servo wrist_ver;
Servo gripper;

int xPin = A0; 
int yPin = A1;  
// Butoane
const int btnB = 3;
const int btnD = 5;

int baseAngle = 90;  

void setup() {
  Braccio.begin();

  pinMode(btnB, INPUT_PULLUP);
  pinMode(btnD, INPUT_PULLUP);

  Serial.begin(9600);
}

void loop() {
  int xVal = analogRead(xPin); 
  int yVal = analogRead(yPin);  

  int shoulderAngle = map(xVal, 0, 1023, 15, 165);  
  int elbowAngle    = map(yVal, 0, 1023, 0, 180);  

  // Verificăm butoanele
  if (digitalRead(btnB) == LOW) {
    baseAngle -= 20;  
  }
  if (digitalRead(btnD) == LOW) {
    baseAngle += 20; 
  }

  baseAngle = constrain(baseAngle, 0, 180);

  // Mișcare a brațului
  Braccio.ServoMovement(20, 
    baseAngle,       
    shoulderAngle,    
    elbowAngle,       
    90,               
    90,               
    10                
  );

  // Debug serial
  Serial.print("Base: "); Serial.print(baseAngle);
  Serial.print(" | Umăr: "); Serial.print(shoulderAngle);
  Serial.print(" | Cot: "); Serial.println(elbowAngle);

  delay(50);  
}