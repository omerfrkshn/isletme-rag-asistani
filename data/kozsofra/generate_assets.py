"""Catering broşürü (PDF) ve el yazısı not (görsel) demo dosyalarını üretir.

Kullanım:
    python data/kozsofra/generate_assets.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

OUT_DIR = Path(__file__).parent

# Türkçe karakterler için Helvetica yetmiyor (WinAnsi'de ş/ğ/ı yok) — Arial TTF gömüyoruz.
pdfmetrics.registerFont(TTFont("Arial", "C:/Windows/Fonts/arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", "C:/Windows/Fonts/arialbd.ttf"))


def make_catering_pdf() -> None:
    path = OUT_DIR / "catering_brosuru.pdf"
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4

    def line(y, text, size=11, bold=False):
        c.setFont("Arial-Bold" if bold else "Arial", size)
        c.drawString(2 * cm, y, text)

    y = height - 2.5 * cm
    line(y, "Köz Sofra Restoran Grubu — Catering ve Özel Gün Broşürü", 16, bold=True)
    y -= 1.2 * cm
    line(y, "Doğum Günü Paketleri", 13, bold=True)
    y -= 0.7 * cm
    line(y, "Küçük Paket (10-15 kişi) — Kişi başı 450 TL", 11)
    y -= 0.5 * cm
    line(y, "  Başlangıçlar + ana yemek seçimi + tatlı ikramı + pasta servisi.")
    y -= 0.6 * cm
    line(y, "Büyük Paket (16-30 kişi) — Kişi başı 550 TL", 11)
    y -= 0.5 * cm
    line(y, "  Küçük paket + özel dekorasyon + fotoğraf köşesi.")
    y -= 1 * cm
    line(y, "Kurumsal Etkinlikler", 13, bold=True)
    y -= 0.7 * cm
    line(y, "20 kişi ve üzeri kurumsal rezervasyonlarda özel menü hazırlanır,")
    y -= 0.5 * cm
    line(y, "fatura kesimi yapılır. Minimum harcama tutarı şubeye göre değişir.")
    y -= 1 * cm
    line(y, "Nişan ve Kına Organizasyonları", 13, bold=True)
    y -= 0.7 * cm
    line(y, "Ataşehir şubemizin bahçe alanı 40 kişiye kadar özel etkinliklere")
    y -= 0.5 * cm
    line(y, "kapatılabilir. Rezervasyon için en az 2 hafta önceden başvurun.")
    y -= 1 * cm
    line(y, "İletişim: catering@kozsofra.example — 0212 555 01 02", 11, bold=True)

    c.showPage()
    c.save()
    print(f"Yazıldı: {path}")


def make_handwritten_note_image() -> None:
    path = OUT_DIR / "el_yazisi_not.png"
    img = Image.new("RGB", (900, 500), color="#fdf6e3")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("C:/Windows/Fonts/comic.ttf", 28)
    except OSError:
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 28)

    lines = [
        "Not (mutfak defterinden):",
        "",
        "Cuma aksami masa 7 icin ozel istek -",
        "misafir findik alerjisi var, kunefe",
        "yerine kazandibi hazirlanacak.",
        "",
        "Ayrica masa 7 dogum gunu, mum",
        "istiyorlar - resepsiyona haber ver.",
        "",
        "- Sef Ahmet",
    ]

    y = 40
    for text_line in lines:
        draw.text((40, y), text_line, fill="#1a1a1a", font=font)
        y += 45

    img.save(path)
    print(f"Yazıldı: {path}")


if __name__ == "__main__":
    make_catering_pdf()
    make_handwritten_note_image()
