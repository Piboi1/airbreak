// Airbrake: Arduino Uno R3 + 9g servo on pin 9.
// Waits 60 s after power-up (or reset), opens once, and stays open. It never closes again;
// reset or power-cycle the Uno to start over. Wiring: orange -> pin 9, red -> 5V, brown -> GND.
// Same angles and direction as servo_test.ino.

#include <Servo.h>

const uint8_t SERVO_PIN = 9;
const int CLOSED_DEG = 0;                 // fins retracted (start position)
const int OPEN_DEG   = 66;                // fins fully out
const bool REVERSED  = true;              // mirror every angle, same as servo_test.ino
const unsigned long DELAY_MS = 60000UL;   // wait before opening

Servo servo;

void setup() {
  Serial.begin(115200);
  servo.attach(SERVO_PIN);
  servo.write(REVERSED ? 180 - CLOSED_DEG : CLOSED_DEG);   // start closed
  Serial.println(F("Closed. Opening in 60 s..."));
  delay(DELAY_MS);
  servo.write(REVERSED ? 180 - OPEN_DEG : OPEN_DEG);       // straight to open at full speed
  Serial.println(F("Open. Staying open."));
}

void loop() {
  // Nothing: the servo stays attached, so it keeps holding the open position.
}
