
/*
  simpleMovements.ino

 The simpleMovements sketch shows how to move each servo motor of the Braccio

 Created on 18 Nov 2015
 by Andrea Martino

 This example is in the public domain.
 */

#include <Braccio.h>
#include <Servo.h>
#include <ArduinoJson.h>

#define UART_BAUDRATE 9600

Servo base;
Servo shoulder;
Servo elbow;
Servo wrist_rot;
Servo wrist_ver;
Servo gripper;
int nr=0;

void setup() {
  //Initialization functions and set up the initial position for Braccio
  //All the servo motors will be positioned in the "safety" position:
  //Base (M1):90 degrees
  //Shoulder (M2): 45 degrees
  //Elbow (M3): 180 degrees
  //Wrist vertical (M4): 180 degrees
  //Wrist rotation (M5): 90 degrees
  //gripper (M6): 10 degrees
  Serial.begin(9600);       // Pentru monitor serial (USB)
  Serial1.begin(UART_BAUDRATE);  // Pentru comunicare cu Uno R4 WiFi pe pinii 18 (TX1) și 19 (RX1)
  Serial.println("Mega 2560 UART Receiver is ready...");
  Braccio.begin();
  Braccio.ServoMovement(30, 45, 70, 35, 90, 90, 73);
}

void loop() {
   

   if (Serial1.available() > 0) {
    String receivedData = Serial1.readString();
    Serial.print("Received data from Uno R4 WiFi: ");
    Serial.println(receivedData);

    // Allocate a JSON document
    StaticJsonDocument<200> doc;

    // Parse the JSON string
    DeserializationError error = deserializeJson(doc, receivedData);

    if (error) {
      Serial.print("JSON parse failed: ");
      Serial.println(error.c_str());
      return;
    }

    // Extract variables
    int M1 = doc["M1"];
    int M2 = doc["M2"];
    int M3 = doc["M3"];
    int M4 = doc["M4"];
    int M5 = doc["M5"];
    int M6 = doc["M6"];

    // Print them
    Serial.print("M1: "); Serial.println(M1);
    Serial.print("M2: "); Serial.println(M2);
    Serial.print("M3: "); Serial.println(M3);
    Serial.print("M4: "); Serial.println(M4);
    Serial.print("M5: "); Serial.println(M5);
    Serial.print("M6: "); Serial.println(M6);
    Braccio.ServoMovement(20,           M1,  M2, M3, M4, M5,  M6); 

  }
  
                      
}



// #include <Braccio.h>
// #include <Servo.h>
// #include <ArduinoJson.h>

// #define UART_BAUDRATE 9600

// Servo base;
// Servo shoulder;
// Servo elbow;
// Servo wrist_rot;
// Servo wrist_ver;
// Servo gripper;
// int nr=0;
// int nr1=0;

// void setup() {
//   //Initialization functions and set up the initial position for Braccio
//   //All the servo motors will be positioned in the "safety" position:
//   //Base (M1):90 degrees
//   //Shoulder (M2): 45 degrees
//   //Elbow (M3): 180 degrees
//   //Wrist vertical (M4): 180 degrees
//   //Wrist rotation (M5): 90 degrees
//   //gripper (M6): 10 degrees
//   Serial.begin(9600);       // Pentru monitor serial (USB)
//   // Serial1.begin(UART_BAUDRATE);  // Pentru comunicare cu Uno R4 WiFi pe pinii 18 (TX1) și 19 (RX1)
//   // Serial.println("Mega 2560 UART Receiver is ready...");
//   Braccio.begin();
// }
// void writeLetterA() { Serial.println("Writing A"); }
// void writeLetterB() { Serial.println("Writing B"); }
// void writeLetterC() { Serial.println("Writing C"); }
// void writeLetterD() { Serial.println("Writing D"); }
// void writeLetterE() { Serial.println("Writing E"); }
// void writeLetterF() { Serial.println("Writing F"); }
// void writeLetterG() { Serial.println("Writing G"); }
// void writeLetterH() { Serial.println("Writing H"); }
// void writeLetterI() { Serial.println("Writing I"); }
// void writeLetterJ() { Serial.println("Writing J"); }
// void writeLetterK() { Serial.println("Writing K"); }
// void writeLetterL() { Serial.println("Writing L"); }
// void writeLetterM() { Serial.println("Writing M"); }
// void writeLetterN() { Serial.println("Writing N"); }
// void writeLetterO() { Serial.println("Writing O"); }
// void writeLetterP() { Serial.println("Writing P"); }
// void writeLetterQ() { Serial.println("Writing Q"); }
// void writeLetterR() { Serial.println("Writing R"); }
// void writeLetterS() { Serial.println("Writing S");
//   Braccio.ServoMovement(20,           90,  100, 0, 10, 180,  73);
//  }
// void writeLetterT() { Serial.println("Writing T"); }
// void writeLetterU() { Serial.println("Writing U"); }
// void writeLetterV() { Serial.println("Writing V"); }
// void writeLetterW() { Serial.println("Writing W"); }
// void writeLetterX() { Serial.println("Writing X"); }
// void writeLetterY() { Serial.println("Writing Y"); }
// void writeLetterZ() { Serial.println("Writing Z"); }
// void writeLetter1() { Serial.println("Writing 1"); 
//   nr=100000;
//   while(nr>=0){
//     nr=nr-1;
//   Braccio.ServoMovement(20,10,  90, 0, 90, 90,  80);
//   delay(1000);
//   Braccio.ServoMovement(20,0,  80, 0, 90, 90,  15);
//   delay(1000);
//   }

// }

// void processLetter(char letter) {
//   switch (letter) {
//     case 'A':
//       writeLetterA();
//       break;
//     case 'B':
//       writeLetterB();
//       break;
//     case 'C':
//       writeLetterC();
//       break;
//     case 'D':
//       writeLetterD();
//       break;
//     case 'E':
//       writeLetterE();
//       break;
//     case 'F':
//       writeLetterF();
//       break;
//     case 'G':
//       writeLetterG();
//       break;
//     case 'H':
//       writeLetterH();
//       break;
//     case 'I':
//       writeLetterI();
//       break;
//     case 'J':
//       writeLetterJ();
//       break;
//     case 'K':
//       writeLetterK();
//       break;
//     case 'L':
//       writeLetterL();
//       break;
//     case 'M':
//       writeLetterM();
//       break;
//     case 'N':
//       writeLetterN();
//       break;
//     case 'O':
//       writeLetterO();
//       break;
//     case 'P':
//       writeLetterP();
//       break;
//     case 'Q':
//       writeLetterQ();
//       break;
//     case 'R':
//       writeLetterR();
//       break;
//     case 'S':
//       writeLetterS();
//       break;
//     case 'T':
//       writeLetterT();
//       break;
//     case 'U':
//       writeLetterU();
//       break;
//     case 'V':
//       writeLetterV();
//       break;
//     case 'W':
//       writeLetterW();
//       break;
//     case 'X':
//       writeLetterX();
//       break;
//     case 'Y':
//       writeLetterY();
//       break;
//     case 'Z':
//       writeLetterZ();
//       break;
//     case '1':
//       writeLetter1();
//       break;
//     default:
//       Serial.println("Unknown letter");
//       break;
//   }
// }

// void draw1() {
//   Braccio.ServoMovement(30, 0, 80, 25, 90, 90, 73); //jos
//   delay(500);
//   Braccio.ServoMovement(30, 0, 90, 15, 90, 90, 73); //jos
//   delay(500);
// }
// void draw2() {
//   // 1. Linie orizontală sus (stânga → dreapta)
//   Braccio.ServoMovement(30, 0, 70, 35, 90, 90, 73); //pornire
//   delay(500);
//   Braccio.ServoMovement(30, 22, 70, 35, 90, 90, 73); //dreapta
//   delay(500);

//   // 2. Linia verticală mică dreapta
//   Braccio.ServoMovement(30, 22, 80, 25, 90, 90, 73); //jos
//   delay(500);

//   // 3. Diagonală stânga-jos
//   Braccio.ServoMovement(30, 0, 80, 25, 90, 90, 73); //stanga
//   delay(500);

//   // 4. Linie orizontală jos (stânga → dreapta)
//   Braccio.ServoMovement(30, 0, 90, 15, 90, 90, 73); //jos
//   delay(500);

//   // Ridică pixul
//   Braccio.ServoMovement(30, 22, 90, 15, 90, 90, 73);//dreapta
//   delay(300);
// }

// void draw0() {
//   // 1. Linie orizontală sus (stânga → dreapta)
//   Braccio.ServoMovement(30, 0, 70, 35, 90, 90, 73); //pornire coltul stanga sus
//   delay(500);
//   Braccio.ServoMovement(30, 22, 70, 35, 90, 90, 73); //dreapta sus
//   delay(500);
//   Braccio.ServoMovement(30, 22, 80, 25, 90, 90, 73); //jos
//   delay(500);
//   Braccio.ServoMovement(30, 22, 90, 15, 90, 90, 73); //jos dreapta 
//   delay(500);
//   Braccio.ServoMovement(30, 0,  90, 15, 90, 90, 73); //stanga(coltul din stanga jos)
//   delay(500);
//    Braccio.ServoMovement(30, 0, 70, 35, 90, 90, 73); //pornire(coltul din stanga sus)
//   delay(500);
// }

// void drawY() {
//   // 1. Linie orizontală sus (stânga → dreapta)
//   Braccio.ServoMovement(30, 0, 70, 35, 90, 90, 73); //pornire coltul stanga sus
//   delay(500);
//   Braccio.ServoMovement(30, 0, 80, 25, 90, 90, 73); //jos
//   delay(500);
//   Braccio.ServoMovement(30, 22, 80, 25, 90, 90, 73); //dreapta
//   delay(500);
//   Braccio.ServoMovement(30, 22, 70, 35, 90, 90, 73); //dreapta sus
//   delay(500);
//   Braccio.ServoMovement(30, 22, 90, 15, 90, 90, 73); //jos dreapta 
//   delay(500);
//   Braccio.ServoMovement(30, 0,  90, 15, 90, 90, 73); //stanga(coltul din stanga jos)
//   delay(500);
// }

// void drawE() {

//   Braccio.ServoMovement(30, 22, 70, 35, 90, 90, 73); //dreapta sus
//   delay(500);
//   Braccio.ServoMovement(30, 0, 70, 35, 90, 90, 73); //pornire coltul stanga sus
//   delay(500);
//   Braccio.ServoMovement(30, 0, 80, 25, 90, 90, 73); //mijloc stanga
//   delay(500);
//   Braccio.ServoMovement(30, 22, 80, 25, 90, 90, 73); //mijloc dreapta
//   delay(500);
//   Braccio.ServoMovement(30, 0, 80, 25, 90, 90, 73); //mijloc stanga
//   delay(500);
//   Braccio.ServoMovement(30, 0, 90, 15, 90, 90, 73); //jos
//   delay(500);
//   Braccio.ServoMovement(30, 22, 90, 15, 90, 90, 73); //jos dreapta 
//   delay(500);
// }

// void drawA() {

//   Braccio.ServoMovement(30, 0,  90, 15, 90, 90, 73); //stanga(coltul din stanga jos)
//   delay(500);
//    Braccio.ServoMovement(30, 0, 70, 35, 90, 90, 73); //coltul stanga sus
//   delay(500);
//   Braccio.ServoMovement(30, 22, 70, 35, 90, 90, 73); //dreapta sus
//   delay(500);
//     Braccio.ServoMovement(30, 22, 80, 25, 90, 90, 73); //mijloc dreapta
//   delay(500);
//   Braccio.ServoMovement(30, 0, 80, 25, 90, 90, 73); //mijloc stanga
//   delay(500);
//   Braccio.ServoMovement(30, 22, 80, 25, 90, 90, 73); //mijloc dreapta
//   delay(500);
//   Braccio.ServoMovement(30, 22, 90, 15, 90, 90, 73); //jos dreapta 
//   delay(500);
  
// }

// void drawR() {

//   Braccio.ServoMovement(30, 0,  90, 15, 90, 90, 73); //stanga(coltul din stanga jos)
//   delay(500);
//    Braccio.ServoMovement(30, 0, 70, 35, 90, 90, 73); //coltul stanga sus
//   delay(500);
//   Braccio.ServoMovement(30, 22, 70, 35, 90, 90, 73); //dreapta sus
//   delay(500);
//     Braccio.ServoMovement(30, 22, 80, 25, 90, 90, 73); //mijloc dreapta
//   delay(500);
//   Braccio.ServoMovement(30, 0, 80, 25, 90, 90, 73); //mijloc stanga
//   delay(500);
//   Braccio.ServoMovement(30, 22, 90, 15, 90, 90, 73); //jos dreapta 
//   delay(500);
  
// }

// void drawS() {

//   Braccio.ServoMovement(30, 22, 70, 35, 90, 90, 73); //dreapta sus
//   delay(500);
//    Braccio.ServoMovement(30, 0, 70, 35, 90, 90, 73); //coltul stanga sus
//   delay(500);
//   Braccio.ServoMovement(30, 0, 80, 25, 90, 90, 73); //mijloc stanga
//   delay(500);
//   Braccio.ServoMovement(30, 22, 80, 25, 90, 90, 73); //mijloc dreapta
//   delay(500);
//   Braccio.ServoMovement(30, 22, 90, 15, 90, 90, 73); //jos dreapta 
//   delay(500);
//   Braccio.ServoMovement(30, 0,  90, 15, 90, 90, 73); //stanga(coltul din stanga jos)
//   delay(500);
  
// }





// void loop() {

//   // if(nr == 0){
//   //   processLetter('S');
//   //   Braccio.ServoMovement(20,90, 90, 90, 90, 90,  50);
//   //   nr=nr +1;
//   //   delay(1000);
//   //    Braccio.ServoMovement(20,90, 90, 90, 90, 90,  50);
//   // }
//   //  processLetter('S');


//     // Braccio.ServoMovement(30,           0,  80, 25, 90, 90,  50);
//     // nr=nr +1;
//     // delay(1000);
//     // Braccio.ServoMovement(30,           0,  80, 25, 90, 90,  73);
//     //  delay(1000);
//     // // processLetter('1');
//     // // delay(10000);
//     // if(nr1==0){
//     //   Braccio.ServoMovement(30,           20,  60, 45, 90, 90,  73);
//     //   delay(1000);
//     //   Braccio.ServoMovement(30,           20,  80, 25, 90, 90,  73);
//     //   delay(500);
//     //   Braccio.ServoMovement(30,           20,  100, 5, 90, 90,  73);
//     //   delay(1000);
//     // }30, 0, 70, 35, 90, 90, 73
//   Braccio.ServoMovement(30, 0, 70, 35, 90, 90, 0);//ia pix
//    delay(500);
//    Braccio.ServoMovement(30, 0, 70, 35, 90, 90, 73);
//   delay(2000);

//   drawR();
//   delay(1500);
//    Braccio.ServoMovement(30, 0, 80, 45, 90, 90, 73);// pozitia de start cu pixul ridicat
//    delay(500);
//   Braccio.ServoMovement(30, 0, 80, 25, 90, 90, 73); //coboara iar pixul pe foaie   
//    delay(2000);

//    draw1();
//    delay(1500);
//    Braccio.ServoMovement(30, 0, 80, 45, 90, 90, 73);// pozitia de start cu pixul ridicat
//    delay(500);
//   Braccio.ServoMovement(30, 0, 80, 25, 90, 90, 73); //coboara iar pixul pe foaie   
//    delay(2000);

//    draw2();
//    Braccio.ServoMovement(30, 0, 80, 45, 90, 90, 73);// pozitia de start cu pixul ridicat
//    delay(500);
//   Braccio.ServoMovement(30, 0, 80, 25, 90, 90, 73); //coboara iar pixul pe foaie  
//    delay(2000);

//    draw0();
//  delay(2000);
//   Braccio.ServoMovement(30, 0, 80, 45, 90, 90, 73);// pozitia de start cu pixul ridicat
//    delay(500);
//   Braccio.ServoMovement(30, 0, 80, 25, 90, 90, 73); //coboara iar pixul pe foaie 


//   drawY();
//  delay(2000);
//   Braccio.ServoMovement(30, 0, 80, 45, 90, 90, 73);// pozitia de start cu pixul ridicat
//    delay(500);
//   Braccio.ServoMovement(30, 0, 80, 25, 90, 90, 73); //coboara iar pixul pe foaie 
//     //  Braccio.ServoMovement(20,           0,  100, 10,15, 90,  50);

//     drawE();
//  delay(2000);
//   Braccio.ServoMovement(30, 0, 80, 45, 90, 90, 73);// pozitia de start cu pixul ridicat
//    delay(500);
//   Braccio.ServoMovement(30, 0, 80, 25, 90, 90, 73); //coboara iar pixul pe foaie 

//     drawA();
//  delay(2000);
//   Braccio.ServoMovement(30, 0, 80, 45, 90, 90, 73);// pozitia de start cu pixul ridicat
//    delay(500);
//   Braccio.ServoMovement(30, 0, 80, 25, 90, 90, 73); //coboara iar pixul pe foaie 

//     drawR();
//  delay(2000);
//   Braccio.ServoMovement(30, 0, 80, 45, 90, 90, 73);// pozitia de start cu pixul ridicat
//    delay(500);
//   Braccio.ServoMovement(30, 0, 80, 25, 90, 90, 73); //coboara iar pixul pe foaie 

//    drawS();
//  delay(2000);
//   Braccio.ServoMovement(30, 0, 80, 45, 90, 90, 73);// pozitia de start cu pixul ridicat
//    delay(500);
//   Braccio.ServoMovement(30, 0, 80, 25, 90, 90, 73); //coboara iar pixul pe foaie 
// }



