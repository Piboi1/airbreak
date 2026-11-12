// Airbrake servo on an ESP32, powered by a 1S LiPo through a 5 V boost converter.
// Press keys to drive it, two ways:
//   1) USB cable + Serial Monitor (115200 baud): type  o  (open),  c  (close),  s  (sweep), or a number 0..180, then Enter.
//   2) Wireless: join WiFi "AIRBRAKE" (password airbrake123), open http://192.168.4.1 and just press  o  or  c  on the keyboard
//      (or tap the buttons).
//
// Wiring:
//   boost OUT+ (5 V) -> servo red  AND  ESP32 5V/VIN pin
//   boost OUT- (GND) -> servo brown AND ESP32 GND        (LiPo + / - go to the boost converter INPUT)
//   servo orange (signal) -> GPIO 18 on a classic ESP32 DevKit, GPIO 3 (pin D1) on a XIAO ESP32-C3
//   100-470 uF capacitor across the servo red/brown wires, near the servo.
// Set the boost converter to 5.0 V with a meter BEFORE connecting the ESP32.
// Needs: ESP32 board package (esp32:esp32) and the ESP32Servo library.

#include <WiFi.h>
#include <WebServer.h>
#include <ESP32Servo.h>

#if defined(CONFIG_IDF_TARGET_ESP32C3)
const int SERVO_PIN = 3;      // XIAO ESP32-C3: D1
#else
const int SERVO_PIN = 18;     // classic ESP32 DevKit
#endif

const char* AP_SSID = "AIRBRAKE";
const char* AP_PASS = "airbrake123";

const int CLOSED_DEG = 0;     // fins retracted
const int OPEN_DEG   = 66;    // fins fully out
const bool REVERSED  = true;  // same direction as the Uno sketches

WebServer server(80);
Servo servo;
int current = CLOSED_DEG;

void moveTo(int target) {                       // straight to the target = full servo speed
  target = constrain(target, 0, 180);
  servo.write(REVERSED ? 180 - target : target);
  current = target;
}

void handleKey(char k) {
  if (k == 'o' || k == 'O')      { moveTo(OPEN_DEG);   Serial.println("open"); }
  else if (k == 'c' || k == 'C') { moveTo(CLOSED_DEG); Serial.println("closed"); }
  else if (k == 's' || k == 'S') { moveTo(OPEN_DEG); delay(400); moveTo(CLOSED_DEG); Serial.println("swept"); }
}

const char PAGE[] PROGMEM = R"HTML(<!doctype html><html><head><meta name=viewport content="width=device-width,initial-scale=1">
<title>Airbrake</title><style>
body{font-family:sans-serif;text-align:center;margin:0;padding:24px;background:#111;color:#eee}
button{display:block;width:100%;font-size:2em;padding:.9em;margin:14px 0;border:0;border-radius:14px;color:#fff}
#o{background:#c0392b}#c{background:#2980b9}#s{font-size:1.2em;opacity:.85}
</style></head><body><h2>Airbrake</h2><p>Press <b>O</b> to open, <b>C</b> to close</p>
<button id=o onclick="go('open')">OPEN (O)</button>
<button id=c onclick="go('close')">CLOSE (C)</button>
<p id=s>ready</p>
<script>
function go(p){fetch('/'+p).then(r=>r.text()).then(t=>document.getElementById('s').textContent=t)
 .catch(()=>document.getElementById('s').textContent='no connection')}
document.addEventListener('keydown',e=>{if(e.repeat)return;const k=e.key.toLowerCase();
 if(k==='o')go('open');else if(k==='c')go('close');});
</script></body></html>)HTML";

void setup() {
  Serial.begin(115200);
  servo.setPeriodHertz(50);
  servo.attach(SERVO_PIN, 500, 2400);
  moveTo(CLOSED_DEG);

  WiFi.mode(WIFI_AP);
  WiFi.softAP(AP_SSID, AP_PASS);
  server.on("/", []() { server.send_P(200, "text/html", PAGE); });
  server.on("/open",  []() { handleKey('o'); server.send(200, "text/plain", "open"); });
  server.on("/close", []() { handleKey('c'); server.send(200, "text/plain", "closed"); });
  server.on("/angle", []() {
    if (server.hasArg("a")) moveTo(server.arg("a").toInt());
    server.send(200, "text/plain", String("angle ") + current);
  });
  server.begin();
  Serial.print("o=open c=close s=sweep 0..180=angle | WiFi AIRBRAKE, http://");
  Serial.println(WiFi.softAPIP());
}

void loop() {
  server.handleClient();
  if (Serial.available()) {
    char k = Serial.peek();
    if (isDigit(k)) { int a = Serial.parseInt(); moveTo(a); Serial.print("angle "); Serial.println(current); }
    else handleKey(Serial.read());
  }
}
