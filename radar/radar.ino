#include <Servo.h>                          // SG90 için standart servo kütüphanesi

const int TRIG = 9;                         // HC-SR04 Trig → D9
const int ECHO = 10;                        // HC-SR04 Echo → D10
const int SERVO_PIN = 11;                   // SG90 sinyal (turuncu) → D11

const int BAS_ACI = 15;                     // taramanın başı (derece)
const int SON_ACI = 165;                    // taramanın sonu
const int ADIM_MS = 30;                     // her derecede servonun oturma süresi

Servo servo;

int mesafeOlc() {
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH);                 // 10 µs darbe: 8 ultrasonik dalga gönder
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);
  long sure = pulseIn(ECHO, HIGH, 30000);   // yankının gidiş-dönüş süresi (µs), 30 ms'de vazgeç
  return sure * 0.0343 / 2;                 // ses 0,0343 cm/µs; yol iki kat → cm
}

void tara(int aci) {
  servo.write(aci);
  delay(ADIM_MS);
  int cm = mesafeOlc();
  Serial.print(aci);                        // seri port: "açı,mesafe" → radar ekranı
  Serial.print(",");
  Serial.println(cm);
}

void setup() {
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);
  servo.attach(SERVO_PIN);
  Serial.begin(115200);
}

void loop() {
  for (int a = BAS_ACI; a <= SON_ACI; a++) tara(a);  // sağdan sola
  for (int a = SON_ACI; a >= BAS_ACI; a--) tara(a);  // soldan sağa
}
