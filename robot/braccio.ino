#include <Braccio.h>   // Biblioteca oficială Braccio
#include <Servo.h>     // Pentru definiția obiectelor Servo

// ————————————————
// Servo-urile pe care le așteaptă Braccio.ServoMovement()
Servo base;
Servo shoulder;
Servo elbow;
Servo wrist_ver;
Servo wrist_rot;
Servo gripper;

// ————————————————
// Parametri de mișcare
const int STEP_DELAY   = 30;   // ms între pași (smooth dacă e mic)
const int ACTION_DELAY = 50;  // ms pauză după fiecare mișcare

// ————————————————
// Unghiuri pentru gripper
const int GRIP_OPEN   = 10;
const int GRIP_CLOSED = 70;

// ————————————————
// Poziție de pick-up
const int PICK_BASE      = 40;
const int PICK_SHOULDER  = 48;
const int PICK_ELBOW     = 60;
const int PICK_WRISTVER  = 70;
const int PICK_WRISTROT  = 90;

// ————————————————
// Poziție de lift (ridicat sus, fără pivot)
const int RAISE_SHOULDER = 80;
const int RAISE_ELBOW    = 80;
const int RAISE_WRISTVER = 90;

// ————————————————
// Poziție intermediară de siguranță (după eliberare)
const int INTER_BASE     = 80;
const int INTER_SHOULDER = 80;
const int INTER_ELBOW    = 80;
const int INTER_WRISTVER = 80;
const int INTER_WRISTROT = 90;

// ————————————————
// Poziții de drop pentru fiecare culoare (M1–M5)
const int DROP_RED[]    = { 100, 55,  80, 40,  90 };
const int DROP_BLUE[]   = { 118, 55,  80, 40,  90 };
const int DROP_GREEN[]  = { 138, 55,  80, 40,  90 };
const int DROP_YELLOW[] = { 138, 55,  80, 40,  90 };
const int DROP_ORANGE[] = { 100, 55,  80, 40,  90 };
const int DROP_PURPLE[] = { 118, 55,  80, 40,  90 };

void setup() {
  Serial.begin(9600);
  base      .attach(4);
  shoulder  .attach(5);
  elbow     .attach(6);
  wrist_ver .attach(7);
  wrist_rot .attach(8);
  gripper   .attach(9);

  Braccio.begin();

  // Poziția inițială: pick cu gripper deschis
  Braccio.ServoMovement(
    STEP_DELAY,
    PICK_BASE, PICK_SHOULDER, PICK_ELBOW, PICK_WRISTVER, PICK_WRISTROT, GRIP_OPEN
  );
  delay(ACTION_DELAY);
}

void pickAndPlace(const String &color) {
  // 1) Du-te la pick cu gripper deschis
  Braccio.ServoMovement(STEP_DELAY,
    PICK_BASE, PICK_SHOULDER, PICK_ELBOW, PICK_WRISTVER, PICK_WRISTROT, GRIP_OPEN
  );
  delay(ACTION_DELAY);

  // 2) Închide gripper să apuci cubul
  Braccio.ServoMovement(STEP_DELAY,
    PICK_BASE, PICK_SHOULDER, PICK_ELBOW, PICK_WRISTVER, PICK_WRISTROT, GRIP_CLOSED
  );
  delay(ACTION_DELAY);

  // 3) Ridică cubul (schimbă doar umăr, cot, încheietură verticală)
  Braccio.ServoMovement(STEP_DELAY,
    PICK_BASE, RAISE_SHOULDER, RAISE_ELBOW, RAISE_WRISTVER, PICK_WRISTROT, GRIP_CLOSED
  );
  delay(ACTION_DELAY);

  // 4) Pivot la baza poziției de drop (schimbă doar M1)
  int targetBase;
  if      (color == "red")    targetBase = DROP_RED[0];
  else if (color == "blue")   targetBase = DROP_BLUE[0];
  else if (color == "green")  targetBase = DROP_GREEN[0];
  else if (color == "yellow") targetBase = DROP_YELLOW[0];
  else if (color == "orange") targetBase = DROP_ORANGE[0];
  else if (color == "purple") targetBase = DROP_PURPLE[0];
  else                         targetBase = PICK_BASE;

  Braccio.ServoMovement(STEP_DELAY,
    targetBase, RAISE_SHOULDER, RAISE_ELBOW, RAISE_WRISTVER, PICK_WRISTROT, GRIP_CLOSED
  );
  delay(ACTION_DELAY);

  // 5) Coboara la poziția completa de drop (M1–M5)
  if (color == "red") {
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
    Braccio.ServoMovement(STEP_DELAY,
      targetBase, RAISE_SHOULDER, RAISE_ELBOW, RAISE_WRISTVER, PICK_WRISTROT, GRIP_CLOSED
    );
  }
  delay(ACTION_DELAY);

  // 6) Deschide gripper sa eliberezi cubul
  Braccio.ServoMovement(STEP_DELAY,
    targetBase,
    (color=="red"?   DROP_RED[1]    : PICK_SHOULDER),
    (color=="red"?   DROP_RED[2]    : PICK_ELBOW),
    (color=="red"?   DROP_RED[3]    : PICK_WRISTVER),
    (color=="red"?   DROP_RED[4]    : PICK_WRISTROT),
    GRIP_OPEN
  );
  delay(ACTION_DELAY);

  // 7) Miscare intermediara de siguranta dupa eliberare
  Braccio.ServoMovement(STEP_DELAY,
    INTER_BASE, INTER_SHOULDER, INTER_ELBOW, INTER_WRISTVER, INTER_WRISTROT, GRIP_OPEN
  );
  delay(ACTION_DELAY);

  // 8) Revenire la pick cu gripper deschis
  Braccio.ServoMovement(STEP_DELAY,
    PICK_BASE, PICK_SHOULDER, PICK_ELBOW, PICK_WRISTVER, PICK_WRISTROT, GRIP_OPEN
  );
  delay(ACTION_DELAY);
}

void loop() {
  if (!Serial.available()) return;
  String color = Serial.readStringUntil('\n');
  color.trim();
  if (color.length()) {
    Serial.print("Color received: ");
    Serial.println(color);
    pickAndPlace(color);
  }
}
