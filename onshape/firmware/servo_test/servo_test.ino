// Servo bench test for the airbrake: 9g micro servo (SG90 type) on an Arduino Uno R3.
// Wiring: orange = signal -> pin 9, red -> 5V, brown -> GND (see docs/wiring_uno_sg90.png).
//
// Serial Monitor at 115200 baud (newline on):
//   o  -> open position     c  -> closed position
//   s  -> slow sweep closed <-> open, once
//   0..180 -> go to that angle
// Set CLOSED_DEG / OPEN_DEG below to the horn angles that match your rotor,
// and test with the horn OFF the rotor first so nothing gets forced.

#include <Servo.h>

const uint8_t SERVO_PIN = 9;
const int CLOSED_DEG = 0;     // fins retracted (adjust to your horn orientation)
const int OPEN_DEG   = 66;    // fins fully out (the rotor turns about 66 degrees)

Servo servo;
int current = CLOSED_DEG;

void moveTo(int target, int stepDelayMs = 15) {
  target = constrain(target, 0, 180);
  while (current != target) {
    current += (target > current) ? 1 : -1;
    servo.write(current);
    delay(stepDelayMs);
  }
}

void setup() {
  Serial.begin(115200);
  servo.attach(SERVO_PIN);
  servo.write(current);
  delay(500);
  Serial.println(F("o=open c=closed s=sweep 0..180=angle"));
}

void loop() {
  if (!Serial.available()) return;
  char c = Serial.peek();
  if (c == 'o')      { Serial.read(); moveTo(OPEN_DEG);   Serial.println(F("open")); }
  else if (c == 'c') { Serial.read(); moveTo(CLOSED_DEG); Serial.println(F("closed")); }
  else if (c == 's') { Serial.read(); moveTo(OPEN_DEG, 25); delay(500); moveTo(CLOSED_DEG, 25); Serial.println(F("swept")); }
  else if (isDigit(c)) {
    int a = Serial.parseInt();
    moveTo(a);
    Serial.print(F("angle ")); Serial.println(current);
  } else Serial.read();   // swallow newline / junk
}
