"""Radar ekranı: Arduino'nun seri porta yazdığı "açı,mesafe" satırlarını okuyup yarım daire radarda çizer.

Her satır bir ölçüm (ör. "30,22" → 30 derecede 22 cm). Ekranda tarama çizgisi son açıyı gösterir; her açının son
ölçümü nokta olarak kalır ve servo o açıya döndüğünde tazelenir. 0 cm = yankı gelmedi (menzil dışı), çizilmez.

Çalıştırmak için (repo klasöründe):
    python radar_ekrani.py --port COM3              # kartla (Linux: /dev/ttyACM0 · macOS: /dev/cu.usbmodem…)
    python radar_ekrani.py --dosya ornek-olcum.txt  # kart olmadan: örnek kaydı oynat
    python radar_ekrani.py --dosya ornek-olcum.txt --png radar.png   # pencere açmadan tek kare kaydet
"""
import argparse  # Komut satırı seçenekleri
import time  # Kayıt oynatırken bekleme

import numpy as np  # Açı hesapları
import matplotlib  # Çizim

YESIL = "#39ff6a"  # Radar yeşili
ARKA = "#06120a"  # Koyu arka plan


def satir_coz(satir):
    """ "açı,mesafe" satırını (açı, cm) yap; bozuk satırda None döndür (seri port açılışında yarım satır gelebilir)."""
    try:
        aci, cm = satir.strip().split(",")
        return int(aci), int(cm)
    except ValueError:
        return None


def seri_kaynak(port, hiz):
    """Seri porttan satır satır oku (Arduino kodundaki Serial.begin(115200) ile aynı hız)."""
    import serial  # pyserial (yalnız kartla çalışırken gerekir)
    with serial.Serial(port, hiz, timeout=1) as s:
        s.reset_input_buffer()
        while True:
            yield s.readline().decode("ascii", errors="ignore")


def dosya_kaynak(yol, bekle):
    """Kayıt dosyasını oynat: satırlar arasında Arduino'daki gibi ~39 ms bekle (30 ms servo + ölçüm)."""
    while True:
        with open(yol, encoding="utf-8") as d:
            for satir in d:
                time.sleep(bekle)
                yield satir


def ekran_kur(menzil):
    """Yarım daire radar ekranı: mesafe halkaları, açı çizgileri, tarama çizgisi ve noktalar."""
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(9, 5.2), facecolor=ARKA)
    ax = fig.add_axes([0.03, 0.12, 0.94, 0.86], projection="polar", facecolor=ARKA)  # Yarım daire pencereyi doldursun
    ax.set_thetamin(0)
    ax.set_thetamax(180)  # 0° sağda, 180° solda (servo sağdan sola tarar)
    ax.set_ylim(0, menzil)
    ax.set_rticks(np.linspace(0, menzil, 5)[1:])
    ax.set_yticklabels([f"{int(r)} cm" for r in np.linspace(0, menzil, 5)[1:]], fontsize=8)
    ax.tick_params(axis="y", colors=YESIL)
    ax.set_thetagrids(range(0, 181, 30), [f"{a}°" for a in range(0, 181, 30)], color=YESIL)
    ax.grid(color=YESIL, alpha=0.3)
    ax.spines["polar"].set_color(YESIL)
    cizgi, = ax.plot([], [], color=YESIL, lw=2)  # Tarama çizgisi
    noktalar = ax.scatter([], [], s=25, color="#ff3b3b", zorder=3)  # Ölçülen nesneler
    yazi = fig.text(0.5, 0.2, "", color=YESIL, ha="center", fontsize=12, family="monospace")
    return fig, cizgi, noktalar, yazi


def main():
    p = argparse.ArgumentParser(description="Arduino radar ekranı")
    kaynak = p.add_mutually_exclusive_group(required=True)
    kaynak.add_argument("--port", help="Arduino'nun seri portu (ör. COM3, /dev/ttyACM0)")
    kaynak.add_argument("--dosya", help='"açı,mesafe" satırları içeren kayıt dosyası')
    p.add_argument("--hiz", type=int, default=115200, help="seri port hızı (varsayılan 115200)")
    p.add_argument("--menzil", type=float, default=40, help="ekranın menzili, cm (varsayılan 40)")
    p.add_argument("--png", help="pencere açmadan, kaydın tamamını çizip bu dosyaya kaydet (yalnız --dosya ile)")
    a = p.parse_args()

    if a.png:
        matplotlib.use("Agg")  # Ekransız çizim
    import matplotlib.pyplot as plt

    olcum = {}  # açı → son mesafe (cm)
    fig, cizgi, noktalar, yazi = ekran_kur(a.menzil)

    def ciz(aci, cm):
        if 0 < cm <= a.menzil:
            olcum[aci] = cm
        else:
            olcum.pop(aci, None)  # Yankı yok ya da menzil dışı: o açıdaki eski noktayı sil
        t = np.radians(aci)
        cizgi.set_data([t, t], [0, a.menzil])
        if olcum:
            noktalar.set_offsets(np.c_[np.radians(list(olcum)), list(olcum.values())])
        yazi.set_text(f"açı {aci:3d}°   mesafe {cm:3d} cm" if cm else f"açı {aci:3d}°   menzil dışı")

    if a.png:
        if not a.dosya:
            p.error("--png yalnız --dosya ile kullanılır")
        with open(a.dosya, encoding="utf-8") as d:
            for satir in d:
                if (o := satir_coz(satir)):
                    ciz(*o)
        fig.savefig(a.png, dpi=120, facecolor=ARKA)
        print(f"{len(olcum)} açıda nesne → {a.png}")
        return

    satirlar = seri_kaynak(a.port, a.hiz) if a.port else dosya_kaynak(a.dosya, 0.039)
    plt.ion()
    plt.show()
    for satir in satirlar:
        if not plt.fignum_exists(fig.number):
            break  # Pencere kapatıldı
        if (o := satir_coz(satir)):
            print(satir.strip())  # Seri monitör gibi
            ciz(*o)
            fig.canvas.draw_idle()
            plt.pause(0.001)


if __name__ == "__main__":
    main()
