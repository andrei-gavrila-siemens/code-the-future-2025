String inputString = "";
bool ledState = false;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW); // Start with LED off
  Serial.begin(9600);
  while (!Serial) {
    ; // Wait for serial port to connect (for Leonardo/Micro)
  }
  Serial.println("Arduino ready - send any data to toggle LED");
}

void loop() {
  if (Serial.available()) {
    char received = Serial.read();
    
    // Toggle LED state
    ledState = !ledState;
    digitalWrite(LED_BUILTIN, ledState ? HIGH : LOW);
    
    // Feedback over serial
    Serial.print("LED is now ");
    Serial.println(ledState ? "ON" : "OFF");
    
    // Optional: clear any remaining data in buffer
    while (Serial.available()) {
      Serial.read();
    }
  }
}