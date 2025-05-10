#include "Arduino_LED_Matrix.h"

ArduinoLEDMatrix matrix;
const int wirePin = 2;
const int wirePinWhite = 7;
bool isConnected = true;

void setup() {
  Serial.begin(115200);
  matrix.begin();
  pinMode(wirePin, INPUT_PULLUP);  // Enable internal pull-up resistor
}

const uint32_t all_on[] = {
    0xFFFFFFFF,  // All LEDs in first row
    0xFFFFFFFF,  // All LEDs in middle row
    0xFFFFFFFF   // All LEDs in last row
};

const uint32_t all_off[] = {
    0x00000000,  // No LEDs in first row
    0x00000000,  // No LEDs in middle row
    0x00000000   // No LEDs in last row
};
  
void loop() {
  // Check if wire is connected (LOW when connected, HIGH when disconnected)
  if (digitalRead(wirePin) == LOW) {
    isConnected = true;
    matrix.loadFrame(all_on);
    delay(1000);
    matrix.loadFrame(all_off);
    delay(1000);

  } else {
    isConnected = false;
    matrix.loadFrame(all_off);  // Turn off all LEDs when wire is disconnected
}
}