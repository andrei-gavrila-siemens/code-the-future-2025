#include <Braccio.h>
#include <Servo.h>

// Inițializare servomotoare
Servo base;
Servo shoulder;
Servo elbow;
Servo wrist_rot;
Servo wrist_ver;
Servo gripper;

// Pini senzor ultrasonic
const int trigPin = 3;
const int echoPin = 2;

long masoaraDistanta();
void apucaObiectRosu(int distanta, int unghiBaza);

void setup() {
  Serial.begin(9600);
  Braccio.begin();
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  // Poziția inițială
  Braccio.ServoMovement(20, 0, 140, 160, 160, 90, 0);
  Serial.println("Sistem pregatit. Asteapta comenzi seriale...");
}

void loop() {


  

      Serial.println("Incep scanarea...");
      for (int unghiBaza = 0; unghiBaza <= 110; unghiBaza += 5) {

          if (Serial.available() > 0) {
      String culoare = Serial.readStringUntil('\n');
      culoare.trim();
      Serial.print("Culoare detectata: ");
      Serial.println(culoare);
        Braccio.ServoMovement(15, unghiBaza, 130, 120, 160, 90, 0);
        delay(300);

        long distanta = masoaraDistanta();
        Serial.print("Unghi baza: ");
        Serial.print(unghiBaza);
        Serial.print(" - Distanta: ");
        Serial.print(distanta);
        Serial.println(" cm");

        if (distanta >= 20 && distanta <= 30 && culoare == "1") {
          Braccio.ServoMovement(15, unghiBaza + 22, 130, 180, 160, 90, 0);
          Serial.println("Obiect detectat! Incep apucarea...");
          apucaObiectRosu(distanta, unghiBaza);
          break;  // oprim căutarea după ce apucăm
        }
        else {
      Serial.println("Eroare: Nu s-a primit culoarea (dupa intarziere)! Va rugam verificati transmisia seriala.");
    }
      }
      // După scanare, așteaptă o nouă comandă
      Serial.println("Scanare completa. Astept noua comanda...");
      delay(1000);

     
    } 

  
}


long masoaraDistanta() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long durata = pulseIn(echoPin, HIGH);
  long distanta = durata * 0.034 / 2;
  return distanta;
}

void apucaObiectRosu(int distanta, int unghiBaza) {
  int unghiUmar = 90;
  int unghiCot = 90;
  int unghiAnte = 180;

  // === Calibrare în funcție de distanță ===
  if (distanta == 20) { unghiUmar = 120; unghiCot = 160; unghiAnte = 145; }
  else if (distanta == 21) { unghiUmar = 125; unghiCot = 160; unghiAnte = 140; }
  else if (distanta == 22) { unghiUmar = 150; unghiCot = 180; unghiAnte = 60; }
  else if (distanta >= 23 && distanta <= 27) { unghiUmar = 150; unghiCot = 180; unghiAnte = 60; }
  else if (distanta >= 28 && distanta <= 30) { unghiUmar = 180; unghiCot = 140; unghiAnte = 75; }
  else { return; }

  // Mergem cu baza la unghiul în care am detectat obiectul
  Braccio.ServoMovement(20, unghiBaza, unghiUmar, 180, 90, 90, 0);
  delay(800);

  // Coborâm brațul către obiect
  Braccio.ServoMovement(20, unghiBaza, unghiUmar, unghiCot, unghiAnte, 90, 0);
  delay(800);

  // Închide gripper-ul
  Braccio.ServoMovement(10, unghiBaza, unghiUmar, unghiCot, unghiAnte, 90, 90);
  delay(800);

  // Ridică obiectul
  Braccio.ServoMovement(10, 0, 90, 90, unghiAnte, 0, 90);
  delay(800);

  // Poziție de eliberare
  Braccio.ServoMovement(10, 0, unghiUmar, unghiCot, unghiAnte, 90, 90);
  delay(800);

  // Deschide gripper-ul
  Braccio.ServoMovement(10, 0, unghiUmar, unghiCot, unghiAnte, 90, 0);
  delay(800);

  // Revine la poziția inițială
  Braccio.ServoMovement(20, 60, 90, 120, 160, 90, 0);
}
