# İşletme Bilgi Asistanı

İşletmenin kendi belgelerine dayanarak müşteri sorularını cevaplayan bir RAG
(Retrieval-Augmented Generation) sistemi.

## Mimari

- **Embedding**: `intfloat/multilingual-e5-small` (lokal, sentence-transformers — API maliyeti yok)
- **Vektör DB**: PostgreSQL + pgvector
- **Cevap üretimi**: Claude API (`claude-sonnet-5`)
- **Formatlar**: düz metin, dijital PDF (PyMuPDF), taranmış/el yazısı görsel (Claude vision)

## Kurulum

```bash
python -m venv .venv
.venv/Scripts/activate  # Windows
pip install -r requirements.txt
cp .env.example .env  # ANTHROPIC_API_KEY doldur
docker compose up -d  # pgvector'lı Postgres
```

## Veri setleri

1. **Köz Sofra Restoran Grubu** (`data/kozsofra/`) — kurgusal demo içerik:
   menü, SSS, politikalar (düz metin), catering broşürü (PDF), mutfak
   defterinden el yazısı not (görsel).
   Demo PDF/görsel dosyalarını üretmek için:
   ```bash
   python data/kozsofra/generate_assets.py
   ```

2. **Türkçe Wikipedia — Türk mutfağı kategorisi** (`data/wikipedia/`) —
   retrieval'ı büyük ölçekte test etmek için:
   ```bash
   python data/wikipedia/fetch_wikipedia.py
   ```

## Besleme (ingestion)

```bash
python -m src.ingest.run_ingest kozsofra data/kozsofra
python -m src.ingest.run_ingest wikipedia data/wikipedia/articles
```

## Sorgulama

```bash
python -m src.query.cli kozsofra "Cumartesi kaça kadar açıksınız?"
```

## Değerlendirme

```bash
python -m src.eval.run_eval
```

Test soru seti `src/eval/eval_dataset.json` içinde; her iki veri seti için
kapsam içi ve kapsam dışı sorular içerir. Sonuçlar `src/eval/eval_results.json`
dosyasına yazılır.

### Sonuçlar

| Veri seti | Retrieval doğruluğu | Halüsinasyon oranı | Soru sayısı |
|---|---|---|---|
| kozsofra | 1.0 | 0.0 | 11 (8 kapsam içi, 3 kapsam dışı) |
| wikipedia | 0.958 | 0.0 | 30 (24 kapsam içi, 6 kapsam dışı) |

- **Retrieval doğruluğu**: kapsam içi sorularda beklenen kaynağın top-k sonuçlarda bulunma oranı.
- **Halüsinasyon oranı**: kapsam dışı sorularda modelin uydurma cevap verme oranı (doğru davranış: "Bu konuda bilgim yok" demek).
- kozsofra veri setinde 3 format da (düz metin, PDF, el yazısı görsel) doğru işlendi ve sorgulandı.
- Not: `retriever.py`'deki benzerlik eşiği (0.78) yalnızca çok alakasız soruları (örn. "Python ne zaman çıktı?") filtreliyor; "Restoranınızda kaç şef çalışıyor?" gibi konuyla ilgili görünen ama kapsam dışı sorularda eşik aşılıyor ve halüsinasyon kontrolü tamamen Claude'un sistem promptuna dayanıyor — bu senaryoda da başarılı oldu.
- **Bilinen retrieval açığı**: "Menemene peynir konur mu?" sorusunda embedding, "peynir" kelimesine ağırlık vererek peynir makalelerini getiriyor, Menemen makalesini değil — model bu yüzden doğru şekilde "bilgim yok" diyor ama asıl kaynağı bulamıyor. Tek bir kelimenin (ürün/malzeme adı) baskın olduğu sorularda embedding tabanlı retrieval'ın bir zaafı olarak not düşüyoruz; bir sonraki adım olarak hybrid search (embedding + anahtar kelime) denenebilir.

**Dürüstlük notu:** Bu, istatistiksel olarak güçlü bir değerlendirme değil — küçük, elle hazırlanmış bir doğrulama kümesi (kozsofra: 11, wikipedia: 30 soru). Amaç kapsamlı bir benchmark değil, üç format işleme yolunun (metin/PDF/görsel), veri seti izolasyonunun ve halüsinasyon önleme mekanizmasının gerçekten çalıştığını göstermek. Wikipedia sorularının bir kısmı bilinçli olarak birbirine yakın yemekler arasında (İmambayıldı/Karnıyarık, kavurma/pastırma, içli köfte/içli pide gibi) ayrım gerektiren zor sorulardan oluşuyor. %100'den farklı bir sonuç (%95.8) çıkması, testin gerçekten zorlayıcı olduğunun bir göstergesi.

## Kapsam dışı (v2 notu)

Görsel-içerik-arama (image similarity search) bu sürümde yok.
