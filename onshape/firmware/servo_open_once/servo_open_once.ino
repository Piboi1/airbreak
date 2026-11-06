// Airbrake open-once test: Arduino Uno R3 + 9g servo on pin 9.
// At power-up or reset the servo goes to CLOSED, waits 45 s, opens once, and stays open (it keeps holding the position).
// Same angles and direction as servo_test.ino. Wiring: orange -> pin 9, red -> 5V, brown -> GND.
// To run it again, press the Uno's reset button (closed again, then 45 s, then open).

#include <Servo.h>

const uint8_t SERVO_PIN = 9;
const int CLOSED_DEG = 0;                 // fins retracted
const int OPEN_DEG   = 66;                // fins fully out
const bool REVERSED  = true;              // mirror every angle, same as servo_test.ino
const unsigned long OPEN_AFTER_MS = 45000UL;

Servo servo;

void setup() {
  Serial.begin(115200);
  servo.attach(SERVO_PIN);
  servo.write(REVERSED ? 180 - CLOSED_DEG : CLOSED_DEG);
  Serial.println(F("Closed. Opening in 45 s."));
}

void loop() {
  static bool opened = false;
  if (!opened && millis() >= OPEN_AFTER_MS) {      // millis() counts from power-up / reset
    servo.write(REVERSED ? 180 - OPEN_DEG : OPEN_DEG);   // straight to open at full servo speed
    opened = true;
    Serial.println(F("Open. Staying open."));
  }
}
