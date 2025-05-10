#include <Braccio.h>   // Biblioteca oficială Braccio
#include <Servo.h>

Servo base;
Servo shoulder;
Servo elbow;
Servo wrist_rot;
Servo wrist_ver;
Servo gripper;

// --- Poziții servo-uri (unghiuri în grade) ---
const int pickPos[5]    = {138,  65,  65,  40,  90};  
const int dropRed[5]    = { 90,  80,  50,  20,  90};
const int dropBlue[5]   = { 30, 120,  80,  60,  90};
const int dropGreen[5]  = {150,  80,  90,  50,  90};
const int dropYellow[5] = {110, 100,  70,  30,  90};
const int dropOrange[5] = { 60, 110,  60,  40,  90};
const int dropPurple[5] = {100,  70, 100,  60,  90};

// Valorile pentru gripper (prin deschis/închis)
const int GRIP_OPEN   = 10;
const int GRIP_CLOSED = 70;

// Mută toate articulațiile în pozițiile date de vectorul pos[]
void moveTo(const int pos[5]) {
  base.write(    pos[0] );   // baza
  shoulder.write(pos[1] );   // umăr
  elbow.write(   pos[2] );   // cot
  wrist_ver.write(pos[3] );   // încheietura (vertical)
  wrist_rot.write(pos[4] );   // încheietura (rotire)
  delay(1000);               // așteaptă finalizarea mișcării
}

// Deschide sau închide gripper-ul
void setGripper(int angle) {
  gripper.write(angle);
  delay(500);
}

// Ridică și plasează cubul în funcție de culoare
void pickAndPlace(const String &color) {
  // 1) Deschide gripper și du brațul la poziția de pick
  setGripper(GRIP_OPEN);
  moveTo(pickPos);

  // 2) Închide gripper ca să prindă cubul
  setGripper(GRIP_CLOSED);
  delay(300);

  // 3) Ridică cubul (revenim în pickPos)
  moveTo(pickPos);

  // 4) Mergi la poziția de drop corespunzătoare culorii
  if (color == "red") {
    moveTo(dropRed);
  } else if (color == "blue") {
    moveTo(dropBlue);
  } else if (color == "green") {
    moveTo(dropGreen);
  } else if (color == "yellow") {
    moveTo(dropYellow);
  } else if (color == "orange") {
    moveTo(dropOrange);
  } else if (color == "purple") {
    moveTo(dropPurple);
  } else {
    // fallback: rămâi în pickPos
    moveTo(pickPos);
  }

  // 5) Eliberează cubul și revino la poziția de start
  setGripper(GRIP_OPEN);
  moveTo(pickPos);
}

void setup() {
  Serial.begin(9600);
  Braccio.begin();           // atașează și inițializează servourile Braccio

  // Poziție inițială: gripper deschis, braț în pickPos
  setGripper(GRIP_OPEN);
  moveTo(pickPos);
}

void loop() {
  if (Serial.available()) {
    String color = Serial.readStringUntil('\n');
    color.trim();
    if (color.length()) {
      Serial.print("Color received: ");
      Serial.println(color);
      pickAndPlace(color);
    }
  }
}
