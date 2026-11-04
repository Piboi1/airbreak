// Servo bench test for the airbrake: 9g micro servo (SG90 type) on an Arduino Uno R3.
// Wiring: orange = signal -> pin 9, red -> 5V, brown -> GND (see docs/wiring_uno_sg90.png).
//
// Serial Monitor at 115200 baud (newline on):
//   o  -> open position     c  -> closed position
//   s  -> one sweep closed -> open -> closed
//   0..180 -> go to that angle (mirrored when REVERSED is true)
// Set CLOSED_DEG / OPEN_DEG below to the horn angles that match your rotor,
// and test with the horn OFF the rotor first so nothing gets forced.

#include <Servo.h>

const uint8_t SERVO_PIN = 9;
const int CLOSED_DEG = 0;     // fins retracted (adjust to your horn orientation)
const int OPEN_DEG   = 66;    // fins fully out (the rotor turns about 66 degrees)
const bool REVERSED  = true;  // true = mirror every angle (servo turns the other way); false = original direction

Servo servo;
int current = CLOSED_DEG;

// Jump straight to the target: the servo moves at its own top speed (an SG90 does about 60 degrees in 0.1 s at 5 V).
// We then wait long enough for it to arrive before accepting the next command.
void moveTo(int target) {
  target = constrain(target, 0, 180);
  int out = REVERSED ? 180 - target : target;
  int travel = abs(target - current);
  servo.write(out);
  current = target;
  delay(travel * 2 + 80);   // about 2 ms per degree, plus a little margin
}

void setup() {
  Serial.begin(115200);
  servo.attach(SERVO_PIN);
  servo.write(REVERSED ? 180 - current : current);
  delay(500);
  Serial.println(F("o=open c=closed s=sweep 0..180=angle"));
}

void loop() {
  if (!Serial.available()) return;
  char c = Serial.peek();
  if (c == 'o')      { Serial.read(); moveTo(OPEN_DEG);   Serial.println(F("open")); }
  else if (c == 'c') { Serial.read(); moveTo(CLOSED_DEG); Serial.println(F("closed")); }
  else if (c == 's') { Serial.read(); moveTo(OPEN_DEG); delay(300); moveTo(CLOSED_DEG); Serial.println(F("swept")); }
  else if (isDigit(c)) {
    int a = Serial.parseInt();
    moveTo(a);
    Serial.print(F("angle ")); Serial.println(current);
  } else Serial.read();   // swallow newline / junk
}
