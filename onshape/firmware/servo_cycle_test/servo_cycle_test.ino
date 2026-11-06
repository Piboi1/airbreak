// Airbrake endurance test: Arduino Uno R3 + 9g servo on pin 9.
// Opens and closes 10 times, waiting 30 s after every move (open, 30 s, close, 30 s, ...), then stops closed.
// Same angles and direction as servo_test.ino. Wiring: orange -> pin 9, red -> 5V, brown -> GND.
// Serial Monitor at 115200 baud prints the cycle count.

#include <Servo.h>

const uint8_t SERVO_PIN = 9;
const int CLOSED_DEG = 0;                 // fins retracted
const int OPEN_DEG   = 66;                // fins fully out
const bool REVERSED  = true;              // mirror every angle, same as servo_test.ino
const int CYCLES = 10;                    // number of open+close cycles
const unsigned long WAIT_MS = 30000UL;    // delay after each open and after each close

Servo servo;
int current = CLOSED_DEG;

// Straight to the target at the servo's own top speed, then wait for it to arrive.
void moveTo(int target) {
  target = constrain(target, 0, 180);
  servo.write(REVERSED ? 180 - target : target);
  delay(abs(target - current) * 2 + 80);
  current = target;
}

void setup() {
  Serial.begin(115200);
  servo.attach(SERVO_PIN);
  servo.write(REVERSED ? 180 - CLOSED_DEG : CLOSED_DEG);
  delay(1000);
  Serial.println(F("Cycle test: 10 x (open, 30 s, close, 30 s)"));

  for (int i = 1; i <= CYCLES; i++) {
    Serial.print(F("Cycle ")); Serial.print(i); Serial.print(F("/")); Serial.print(CYCLES);
    Serial.println(F(": open"));
    moveTo(OPEN_DEG);
    delay(WAIT_MS);
    Serial.println(F("  close"));
    moveTo(CLOSED_DEG);
    delay(WAIT_MS);
  }
  Serial.println(F("Done. Servo left closed."));
  servo.detach();     // stop holding torque and stop any jitter
}

void loop() {
  // nothing: the test runs once at power-up / reset
}
