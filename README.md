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
| wikipedia | 1.0 | 0.0 | 5 (3 kapsam içi, 2 kapsam dışı) |

- **Retrieval doğruluğu**: kapsam içi sorularda beklenen kaynağın top-k sonuçlarda bulunma oranı.
- **Halüsinasyon oranı**: kapsam dışı sorularda modelin uydurma cevap verme oranı (doğru davranış: "Bu konuda bilgim yok" demek).
- kozsofra veri setinde 3 format da (düz metin, PDF, el yazısı görsel) doğru işlendi ve sorgulandı.
- Not: `retriever.py`'deki benzerlik eşiği (0.78) yalnızca çok alakasız soruları (örn. "Python ne zaman çıktı?") filtreliyor; "Restoranınızda kaç şef çalışıyor?" gibi konuyla ilgili görünen ama kapsam dışı sorularda eşik aşılıyor ve halüsinasyon kontrolü tamamen Claude'un sistem promptuna dayanıyor — bu senaryoda da başarılı oldu.

## Kapsam dışı (v2 notu)

Görsel-içerik-arama (image similarity search) bu sürümde yok.
