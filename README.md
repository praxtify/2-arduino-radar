<div align="center">

<img src="docs/kapak.jpg" alt="Masanın radarı — Praxtify" width="100%">

# Arduino ile Ultrasonik Radar · UNO R4 WiFi + SG90 + HC-SR04

**Bir servo, bir ses sensörü ve bir Arduino ile masanın radarını çıkarıyoruz.** SG90 servo, HC-SR04 ultrasonik sensörü
15°'den 165°'ye döndürür. Her derecede yankının dönüş süresinden mesafe hesaplanır ve seri porta `açı,mesafe` olarak yazılır.
Bilgisayardaki **radar ekranı** bu satırları okuyup yarım daire radarda çizer.

[![Arduino](https://img.shields.io/badge/Arduino-UNO%20R4%20WiFi-00878F?logo=arduino&logoColor=white)](https://docs.arduino.cc/hardware/uno-r4-wifi/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Lisans: MIT](https://img.shields.io/badge/Lisans-MIT-green.svg)](LICENSE)
[![YouTube](https://img.shields.io/badge/YouTube-@praxtify-FF0000?logo=youtube&logoColor=white)](https://www.youtube.com/@praxtify)

</div>

<p align="center">
  <img src="docs/tarama.gif" alt="Servo sensörü döndürüyor, sağdaki radar ekranında nesneler beliriyor" width="720">
</p>

---

## İçindekiler

- [Ne öğreneceksin?](#ne-öğreneceksin)
- [Donanım](#donanım)
- [Bağlantılar](#bağlantılar)
- [Kodu karta yükle](#kodu-karta-yükle)
- [Radar ekranı](#radar-ekranı)
- [Proje yapısı](#proje-yapısı)
- [Nasıl çalışıyor?](#nasıl-çalışıyor)
- [Kendin dene](#kendin-dene)
- [Kaynaklar ve lisanslar](#kaynaklar-ve-lisanslar)
- [Praxtify](#praxtify)

## Ne öğreneceksin?

| Konu | Bu projede |
|---|---|
| Ultrasonik ölçüm | HC-SR04'e 10 µs tetik darbesi, `pulseIn` ile yankı süresi, sesin hızıyla santimetre |
| Servo kontrolü | `Servo` kütüphanesiyle SG90'ı derece derece çevirme |
| Seri haberleşme | Her ölçümü `açı,mesafe` satırı olarak bilgisayara gönderme |
| Görselleştirme | Seri port satırlarını Python'da yarım daire radar ekranına çizme |

Arduino kodunun tamamı **tek dosya, 42 satır**: [`radar/radar.ino`](radar/radar.ino). Videoda anlatılan kodla birebir aynıdır.

## Donanım

| Parça | Görevi |
|---|---|
| **Arduino UNO R4 WiFi** | Servoyu çevirir, sensörü tetikler, ölçümü seri porta yazar |
| **SG90 mikro servo** | Sensörü 15°–165° arasında döndürür |
| **HC-SR04 ultrasonik sensör** | Ses dalgası gönderir, yankının dönüş süresini verir (yaklaşık 2–400 cm) |
| **Breadboard** | 5 V ve GND hatlarını paylaştırır |
| Jumper kablolar + 3'lü pin başlığı | Bağlantılar |
| USB-C kablo | Güç ve seri port |

Sensör, servonun koluna takılır; servo döndükçe sensör de etrafı tarar.

## Bağlantılar

<p align="center"><img src="docs/baglanti.jpg" alt="Arduino, breadboard, SG90 ve HC-SR04 bağlantıları" width="720"></p>

| Nereden | Nereye | Kablo |
|---|---|---|
| Arduino **5V** | Breadboard **+** hattı | kırmızı |
| Arduino **GND** | Breadboard **−** hattı | siyah |
| SG90 kahverengi (GND) | **−** hattı | siyah |
| SG90 kırmızı (5V) | **+** hattı | kırmızı |
| SG90 turuncu (sinyal) | Arduino **D11** | turuncu |
| HC-SR04 **VCC** | **+** hattı | kırmızı |
| HC-SR04 **GND** | **−** hattı | siyah |
| HC-SR04 **Trig** | Arduino **D9** | sarı |
| HC-SR04 **Echo** | Arduino **D10** | yeşil |

Servonun fişi breadboard'daki 3'lü pin başlığına geçer; kablolar başlığın yanındaki deliklerden hatlara gider.
Son olarak USB-C kablosunu tak: hem güç hem seri port bu kablodan geçer.

> [!TIP]
> SG90 hareket ederken anlık akım çeker. Servo titrerse ya da Arduino yeniden başlıyorsa servonun + ve − uçlarını ayrı bir
> 5 V kaynağa bağla (toprağı Arduino ile ortak tut).

## Kodu karta yükle

Arduino IDE kullanıyorsan: **Boards Manager**'dan *Arduino UNO R4 Boards*'u kur (`Servo` kütüphanesi IDE ile gelir; yoksa
**Library Manager**'dan kur), `radar/radar.ino`'yu aç, kart olarak *Arduino UNO R4 WiFi*'yi seçip yükle.

Komut satırından ([arduino-cli](https://arduino.github.io/arduino-cli/)):

```bash
git clone https://github.com/praxtify/2-arduino-radar.git
cd 2-arduino-radar

arduino-cli core install arduino:renesas_uno
arduino-cli lib install Servo

arduino-cli compile -b arduino:renesas_uno:unor4wifi radar
arduino-cli upload  -b arduino:renesas_uno:unor4wifi -p <PORT> radar   # Windows: COM3 · Linux: /dev/ttyACM0
```

Derleme çıktısı: program alanının **%20**'si (54 792 / 262 144 bayt). Yükledikten sonra Seri Monitör'ü **115200 baud**'da
açarsan satırları görürsün:

```text
28,22
29,22
30,22
31,22
```

Test edilen ortam: arduino-cli 1.5 · Arduino UNO R4 Boards 1.6.0 · Servo 1.3.0.

## Radar ekranı

[`radar_ekrani.py`](radar_ekrani.py) seri porttan gelen `açı,mesafe` satırlarını okur ve yarım daire radarda çizer.
Tarama çizgisi son açıyı gösterir; her açının son ölçümü kırmızı nokta olarak kalır ve servo o açıya döndüğünde tazelenir.
Yankı gelmeyen ölçümler (`0`) ve menzil dışı noktalar çizilmez.

```bash
python -m venv .venv
# Windows:      .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt

python radar_ekrani.py --port COM3                 # kartla (Linux: /dev/ttyACM0 · macOS: /dev/cu.usbmodem…)
python radar_ekrani.py --dosya ornek-olcum.txt     # kart olmadan: örnek kaydı oynat
```

> [!NOTE]
> Arduino IDE'nin Seri Monitörü açıkken port meşgul olur; radar ekranını çalıştırmadan önce Seri Monitör'ü kapat.

Kart olmadan denemek için [`ornek-olcum.txt`](ornek-olcum.txt) var: videodaki sahnenin bir tam turu (sağdan sola ve geri,
302 ölçüm). Kayıt bittiğinde baştan oynar. Pencere açmadan tek bir görüntü kaydetmek için:

```bash
python radar_ekrani.py --dosya ornek-olcum.txt --png radar.png
```

<p align="center"><img src="docs/radar-ekrani.png" alt="Radar ekranı: dört nesne" width="720"></p>

Görüntüdeki dört nesne videodakilerle aynı: **30°'de kitap** (22 cm), **55°'de teneke** (12 cm), **100°'de meyve suyu kutusu**
(28 cm), **140°'de kupa** (14 cm). Menzili `--menzil 100` gibi değiştirebilirsin (varsayılan 40 cm).

Test edilen ortam: Python 3.13 · Matplotlib 3.11 · NumPy 2.5 · pySerial 3.5 (Windows 11).

## Proje yapısı

```text
2-arduino-radar/
├── radar/
│   └── radar.ino           # Arduino kodu (videodaki)
├── radar_ekrani.py         # seri port → yarım daire radar ekranı
├── ornek-olcum.txt         # kart olmadan denemek için örnek seri port kaydı
├── requirements.txt        # matplotlib, numpy, pyserial (yalnız radar ekranı için)
├── docs/                   # README görselleri
└── LICENSE                 # MIT (proje kodu)
```

## Nasıl çalışıyor?

### 1 · Pinler ve tarama sınırları

```cpp
const int TRIG = 9;                         // HC-SR04 Trig → D9
const int ECHO = 10;                        // HC-SR04 Echo → D10
const int SERVO_PIN = 11;                   // SG90 sinyal (turuncu) → D11

const int BAS_ACI = 15;                     // taramanın başı (derece)
const int SON_ACI = 165;                    // taramanın sonu
const int ADIM_MS = 30;                     // her derecede servonun oturma süresi
```

Tarama 15° ile 165° arasında yapılır. Her derecede servoya 30 ms verilir, yerine otursun; ölçüm ondan sonra alınır.

### 2 · Mesafe ölçümü: sesin gidiş-dönüş süresi

<p align="center"><img src="docs/mesafe-formulu.jpg" alt="mesafeOlc: cm = süre × 0,0343 / 2" width="720"></p>

Trig pinine **10 µs**'lik bir darbe gönderilir; sensör 8 ultrasonik dalga yollar ve dalgalar dönene kadar Echo pinini HIGH
tutar. `pulseIn` bu süreyi mikrosaniye olarak ölçer. Ses saniyede 343 metre, yani mikrosaniyede **0,0343 cm** gider.
Yol gidiş-dönüş olduğu için ikiye bölünür:

$$d\,[\text{cm}] = \frac{t\,[\mu s] \times 0{,}0343}{2}$$

Örneğin 22 cm'deki kitap için yankı yaklaşık 1283 µs'de döner. `pulseIn`'in son parametresi (30 000 µs) bekleme sınırıdır:
yankı 30 ms içinde gelmezse fonksiyon `0` döndürür, mesafe de `0` olur (menzil dışı).

### 3 · `tara()`: çevir, bekle, ölç, yaz

<p align="center"><img src="docs/seri-satir.jpg" alt="Seri port satırı: açı,mesafe → 30,22" width="720"></p>

```cpp
void tara(int aci) {
  servo.write(aci);
  delay(ADIM_MS);
  int cm = mesafeOlc();
  Serial.print(aci);                        // seri port: "açı,mesafe" → radar ekranı
  Serial.print(",");
  Serial.println(cm);
}
```

Her ölçüm tek satır: `30,22` → 30 derecede 22 cm. Bu kadar basit bir biçim sayesinde satırı Seri Monitör'de okumak da,
Python'da `split(",")` ile ayırmak da kolay.

### 4 · Döngü: sağdan sola, soldan sağa

```cpp
void loop() {
  for (int a = BAS_ACI; a <= SON_ACI; a++) tara(a);  // sağdan sola
  for (int a = SON_ACI; a >= BAS_ACI; a--) tara(a);  // soldan sağa
}
```

Servo bir uçtan öbürüne gidip geri döner, her derecede bir ölçüm. Bir yön 151 ölçümdür; her ölçüm 30 ms bekleme ve
ölçüm süresiyle yaklaşık 40 ms sürer, yani bir tam tur (gidiş + dönüş) yaklaşık **12 saniye**.

## Kendin dene

- `ADIM_MS`'i 15 yap: tarama hızlanır ama servo yerine oturmadan ölçerse noktalar kayar mı?
- `BAS_ACI` ve `SON_ACI`'yı 0 ve 180 yap: SG90'ın uçlarında ölçüm nasıl değişiyor?
- Aynı açıda üç ölçüm alıp ortancasını yaz: radar ekranındaki titreşen noktalar azalıyor mu?
- `radar_ekrani.py`'de 20 cm'den yakın nesneleri farklı renkte çiz: masanın "alarm bölgesi".

## Kaynaklar ve lisanslar

Bu repodaki **proje kodu** ([`radar.ino`](radar/radar.ino) ve [`radar_ekrani.py`](radar_ekrani.py)) [MIT lisansı](LICENSE)
ile yayımlanır. Kullanılan kütüphaneler kendi lisanslarıyla gelir ve repoya dahil değildir:

| Bileşen | Kaynak | Lisans | Kurulum |
|---|---|---|---|
| **Servo** Arduino kütüphanesi | [arduino-libraries/Servo](https://github.com/arduino-libraries/Servo) | LGPL-2.1 | IDE ile gelir / Library Manager |
| **Arduino UNO R4 Boards** çekirdeği | [arduino/ArduinoCore-renesas](https://github.com/arduino/ArduinoCore-renesas) | MIT | Boards Manager |
| **Matplotlib** | [matplotlib.org](https://matplotlib.org/) | Matplotlib (PSF tabanlı) | `pip` |
| **NumPy** | [numpy.org](https://numpy.org/) | BSD 3-Clause | `pip` |
| **pySerial** | [pyserial/pyserial](https://github.com/pyserial/pyserial) | BSD 3-Clause | `pip` |

Görsellerdeki 3D modeller yalnız anlatım içindir ve repoda yer almaz. Kablolar ve masadaki nesneler Praxtify tarafından
Blender'da modellendi, Arduino UNO R4 WiFi modeli [GrabCAD](https://grabcad.com/library) topluluğundan alındı.
Şu modeller [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) lisansıyla kullanıldı (sahneye yerleştirildi, ölçeklendi ve render alındı):

| Model | Yazar | Kaynak |
|---|---|---|
| Servomotor SG90 | [Robótica Paraná](https://sketchfab.com/roboticaparana) | [Sketchfab](https://sketchfab.com/3d-models/servomotor-sg90-863b04f543a94b82ad5f660aafd997de) |
| HC-SR04 | [peddintiudaykiran176](https://sketchfab.com/peddintiudaykiran176) | [Sketchfab](https://sketchfab.com/3d-models/hc-sr04-e8a6adcef8fd4f45bf27b8d7718ed489) |
| Breadboard Arduino | [syukurmanhia3](https://sketchfab.com/syukurmanhia3) | [Sketchfab](https://sketchfab.com/3d-models/breadboard-arduino-e98f8d8a0e284b818f7540f118fb2ab5) |

## Praxtify

**Teoriyi pratiğe dönüştürüyoruz.** Robotik, gömülü sistemler ve yapay zekâyı çalışan kodla, adım adım anlatıyoruz.
Bu projenin videosu ve yeni projeler için:

<p align="center">
  <a href="https://praxtify.com"><img src="https://img.shields.io/badge/praxtify.com-Web-111111?style=for-the-badge" alt="praxtify.com"></a>
  <a href="https://www.youtube.com/@praxtify"><img src="https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="YouTube"></a>
  <a href="https://www.instagram.com/praxtify"><img src="https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white" alt="Instagram"></a>
  <a href="https://www.tiktok.com/@praxtify"><img src="https://img.shields.io/badge/TikTok-000000?style=for-the-badge&logo=tiktok&logoColor=white" alt="TikTok"></a>
  <a href="https://x.com/praxtify"><img src="https://img.shields.io/badge/X-000000?style=for-the-badge&logo=x&logoColor=white" alt="X"></a>
  <a href="https://www.threads.net/@praxtify"><img src="https://img.shields.io/badge/Threads-000000?style=for-the-badge&logo=threads&logoColor=white" alt="Threads"></a>
  <a href="https://www.linkedin.com/company/praxtify"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"></a>
  <a href="https://www.facebook.com/praxtify"><img src="https://img.shields.io/badge/Facebook-1877F2?style=for-the-badge&logo=facebook&logoColor=white" alt="Facebook"></a>
  <a href="https://www.pinterest.com/praxtify"><img src="https://img.shields.io/badge/Pinterest-BD081C?style=for-the-badge&logo=pinterest&logoColor=white" alt="Pinterest"></a>
</p>

Soru, hata ya da öneri için bir [issue](../../issues) aç. Projeyi beğendiysen ⭐ vermeyi unutma!

**Serinin önceki projesi:** [1-arduino-robot-kol](https://github.com/praxtify/1-arduino-robot-kol): altı servolu robot kolu tek kabloyla Arduino'dan yönetiyoruz.

**Serinin sıradaki projesi:** engelden kaçan robot: aynı HC-SR04 ve SG90 bu kez tekerlekli bir robotun gözü oluyor. Çok yakında.
