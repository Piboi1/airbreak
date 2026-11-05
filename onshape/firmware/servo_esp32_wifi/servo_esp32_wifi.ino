// Airbrake servo over WiFi: ESP32 makes its own WiFi network, no router needed.
// Phone: join WiFi "AIRBRAKE" (password below), open http://192.168.4.1 and tap OPEN / CLOSE.
//
// Wiring (ESP32 DevKit, powered from a USB power bank):
//   servo orange (signal) -> GPIO 18
//   servo red    (+5V)    -> 5V / VIN pin   (this pin is the USB 5V line)
//   servo brown  (GND)    -> GND
//   100-470 uF capacitor across the servo's red/brown wires, close to the servo (stops brownouts)
//
// Needs: ESP32 board package (esp32:esp32) and the ESP32Servo library.

#include <WiFi.h>
#include <WebServer.h>
#include <ESP32Servo.h>

const char* AP_SSID = "AIRBRAKE";
const char* AP_PASS = "airbrake123";   // at least 8 characters

const int SERVO_PIN  = 18;
const int CLOSED_DEG = 0;      // fins retracted (same meaning as the Uno sketch)
const int OPEN_DEG   = 66;     // fins fully out
const bool REVERSED  = true;   // mirror every angle, same as the Uno sketch

WebServer server(80);
Servo servo;
int current = CLOSED_DEG;

void moveTo(int target) {
  target = constrain(target, 0, 180);
  servo.write(REVERSED ? 180 - target : target);   // straight to the target = full servo speed
  current = target;
}

const char PAGE[] PROGMEM = R"HTML(<!doctype html><html><head><meta name=viewport content="width=device-width,initial-scale=1">
<title>Airbrake</title><style>
body{font-family:sans-serif;text-align:center;margin:0;padding:24px;background:#111;color:#eee}
button{display:block;width:100%;font-size:2.2em;padding:1em;margin:16px 0;border:0;border-radius:14px;color:#fff}
#o{background:#c0392b}#c{background:#2980b9}#s{font-size:1.2em;opacity:.8}
</style></head><body><h2>Airbrake</h2>
<button id=o onclick="go('open')">OPEN</button>
<button id=c onclick="go('close')">CLOSE</button>
<p id=s>ready</p>
<script>function go(p){fetch('/'+p).then(r=>r.text()).then(t=>document.getElementById('s').textContent=t)
.catch(()=>document.getElementById('s').textContent='no connection')}</script>
</body></html>)HTML";

void setup() {
  Serial.begin(115200);
  servo.setPeriodHertz(50);
  servo.attach(SERVO_PIN, 500, 2400);
  moveTo(CLOSED_DEG);

  WiFi.mode(WIFI_AP);
  WiFi.softAP(AP_SSID, AP_PASS);
  Serial.print("WiFi AP up, open http://");
  Serial.println(WiFi.softAPIP());

  server.on("/", []() { server.send_P(200, "text/html", PAGE); });
  server.on("/open",  []() { moveTo(OPEN_DEG);   server.send(200, "text/plain", "open"); });
  server.on("/close", []() { moveTo(CLOSED_DEG); server.send(200, "text/plain", "closed"); });
  server.on("/angle", []() {
    if (server.hasArg("a")) moveTo(server.arg("a").toInt());
    server.send(200, "text/plain", String("angle ") + current);
  });
  server.begin();
}

void loop() {
  server.handleClient();
}
