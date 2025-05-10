#include <Braccio.h>   // Biblioteca oficială Braccio
#include <Servo.h>     // Pentru definiția obiectelor Servo

// ————————————————
// Servo-urile pe care le așteaptă Braccio.ServoMovement()
// (definite manual pentru arhitectura renesas_uno)
Servo base;
Servo shoulder;
Servo elbow;
Servo wrist_ver;
Servo wrist_rot;
Servo gripper;

// ————————————————
// Parametri de mișcare
const int STEP_DELAY   = 10;   // ms între pași (smoother dacă e mic)
const int ACTION_DELAY = 500;  // ms pauză după fiecare mișcare

// ————————————————
// Unghiuri pentru gripper
const int GRIP_OPEN   = 10;
const int GRIP_CLOSED = 70;

// ————————————————
// Poziție de pick-up (unde se apleacă după cub)
// M1(Base)=40, M2(Shoulder)=75, M3(Elbow)=80, M4(WristVer)=40, M5(WristRot)=90, M6(Gripper)=10
const int PICK_BASE      = 40;
const int PICK_SHOULDER  = 48;
const int PICK_ELBOW     = 60;
const int PICK_WRISTVER  = 70;
const int PICK_WRISTROT  = 90;

// ————————————————
// Poziții de drop pentru fiecare culoare (M1–M5)
const int DROP_RED[]    = {  90,  80,  50,  20,  90 };
const int DROP_BLUE[]   = {  30, 120,  80,  60,  90 };
const int DROP_GREEN[]  = { 150,  80,  90,  50,  90 };
const int DROP_YELLOW[] = { 110, 100,  70,  30,  90 };
const int DROP_ORANGE[] = {  60, 110,  60,  40,  90 };
const int DROP_PURPLE[] = { 100,  70, 100,  60,  90 };

void setup() {
  Serial.begin(9600);
  // Definește servo-urile globale pentru Braccio
  base       .attach(4);
  shoulder   .attach(5);
  elbow      .attach(6);
  wrist_ver  .attach(7);
  wrist_rot  .attach(8);
  gripper    .attach(9);

  // Inițializează shield-ul Braccio (soft-start etc.)
  Braccio.begin();

  // Poziția inițială: gripper deschis și braț la pick
  Braccio.ServoMovement(
    STEP_DELAY,
    PICK_BASE, PICK_SHOULDER, PICK_ELBOW, PICK_WRISTVER, PICK_WRISTROT, GRIP_OPEN
  );
  delay(ACTION_DELAY);
}

void pickAndPlace(const String &color) {
  // 1) Du-te la pick cu gripper deschis
  Braccio.ServoMovement(
    STEP_DELAY,
    PICK_BASE, PICK_SHOULDER, PICK_ELBOW, PICK_WRISTVER, PICK_WRISTROT, GRIP_OPEN
  );
  delay(ACTION_DELAY);

  // 2) Închide gripper să apuci cubul
  Braccio.ServoMovement(
    STEP_DELAY,
    PICK_BASE, PICK_SHOULDER, PICK_ELBOW, PICK_WRISTVER, PICK_WRISTROT, GRIP_CLOSED
  );
  delay(ACTION_DELAY);

  // 3) (ridică cubul păstrând aceeași poziție de articulații)
  Braccio.ServoMovement(
    STEP_DELAY,
    PICK_BASE, PICK_SHOULDER, PICK_ELBOW, PICK_WRISTVER, PICK_WRISTROT, GRIP_CLOSED
  );
  delay(ACTION_DELAY);

  // 4) Mergi la poziția de drop pentru culoarea primită
  if (    color == "red") {
    Braccio.ServoMovement(STEP_DELAY,
      DROP_RED[0], DROP_RED[1], DROP_RED[2],
      DROP_RED[3], DROP_RED[4], GRIP_CLOSED
    );
  }
  else if (color == "blue") {
    Braccio.ServoMovement(STEP_DELAY,
      DROP_BLUE[0], DROP_BLUE[1], DROP_BLUE[2],
      DROP_BLUE[3], DROP_BLUE[4], GRIP_CLOSED
    );
  }
  else if (color == "green") {
    Braccio.ServoMovement(STEP_DELAY,
      DROP_GREEN[0], DROP_GREEN[1], DROP_GREEN[2],
      DROP_GREEN[3], DROP_GREEN[4], GRIP_CLOSED
    );
  }
  else if (color == "yellow") {
    Braccio.ServoMovement(STEP_DELAY,
      DROP_YELLOW[0], DROP_YELLOW[1], DROP_YELLOW[2],
      DROP_YELLOW[3], DROP_YELLOW[4], GRIP_CLOSED
    );
  }
  else if (color == "orange") {
    Braccio.ServoMovement(STEP_DELAY,
      DROP_ORANGE[0], DROP_ORANGE[1], DROP_ORANGE[2],
      DROP_ORANGE[3], DROP_ORANGE[4], GRIP_CLOSED
    );
  }
  else if (color == "purple") {
    Braccio.ServoMovement(STEP_DELAY,
      DROP_PURPLE[0], DROP_PURPLE[1], DROP_PURPLE[2],
      DROP_PURPLE[3], DROP_PURPLE[4], GRIP_CLOSED
    );
  }
  else {
    // fallback: rămâi sus cu cubul
    Braccio.ServoMovement(
      STEP_DELAY,
      PICK_BASE, PICK_SHOULDER, PICK_ELBOW, PICK_WRISTVER, PICK_WRISTROT, GRIP_CLOSED
    );
  }
  delay(ACTION_DELAY);

  // 5) Deschide gripper să eliberezi
  Braccio.ServoMovement(
    STEP_DELAY,
    // rămâi în poziția de drop (sau PICK dacă vrei)
    (color=="red"?   DROP_RED[0]  : PICK_BASE),
    (color=="red"?   DROP_RED[1]  : PICK_SHOULDER),
    (color=="red"?   DROP_RED[2]  : PICK_ELBOW),
    (color=="red"?   DROP_RED[3]  : PICK_WRISTVER),
    (color=="red"?   DROP_RED[4]  : PICK_WRISTROT),
    GRIP_OPEN
  );
  delay(ACTION_DELAY);

  // 6) Revenire la pick cu gripper deschis
  Braccio.ServoMovement(
    STEP_DELAY,
    PICK_BASE, PICK_SHOULDER, PICK_ELBOW, PICK_WRISTVER, PICK_WRISTROT, GRIP_OPEN
  );
  delay(ACTION_DELAY);
}

void loop() {
  if (!Serial.available()) return;
  String color = Serial.readStringUntil('\n');
  color.trim();
  if (color.length()>0) {
    Serial.print("Color received: ");
    Serial.println(color);
    pickAndPlace(color);
  }
}
