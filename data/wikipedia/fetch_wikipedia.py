"""Türkçe Wikipedia'dan 'Türk mutfağı' kategorisindeki maddeleri indirir.

Kullanım:
    python data/wikipedia/fetch_wikipedia.py
"""

import re
import time
from pathlib import Path

import requests

API_URL = "https://tr.wikipedia.org/w/api.php"
CATEGORY = "Kategori:Türk mutfağı"
OUT_DIR = Path(__file__).parent / "articles"
MAX_ARTICLES = 150

# Wikimedia API, tarayıcı taklidi yapmayan varsayılan User-Agent'ları 403 ile reddediyor.
HEADERS = {"User-Agent": "IsletmeBilgiAsistani/1.0 (demo RAG stres testi; local dev project)"}


def list_category_members(category: str, limit: int) -> list[str]:
    titles: list[str] = []
    cmcontinue = None
    while len(titles) < limit:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": category,
            "cmlimit": "500",
            "cmtype": "page",
            "format": "json",
        }
        if cmcontinue:
            params["cmcontinue"] = cmcontinue

        for attempt in range(5):
            resp = requests.get(API_URL, params=params, headers=HEADERS, timeout=30)
            if resp.status_code == 429:
                time.sleep(5 * (attempt + 1))
                continue
            resp.raise_for_status()
            break
        else:
            raise RuntimeError("429 nedeniyle kategori listesi alınamadı")
        data = resp.json()

        titles.extend(m["title"] for m in data["query"]["categorymembers"])

        cmcontinue = data.get("continue", {}).get("cmcontinue")
        if not cmcontinue:
            break

    return titles[:limit]


def fetch_plaintext(title: str) -> str:
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": "1",
        "titles": title,
        "format": "json",
    }
    for attempt in range(5):
        resp = requests.get(API_URL, params=params, headers=HEADERS, timeout=30)
        if resp.status_code == 429:
            time.sleep(5 * (attempt + 1))
            continue
        resp.raise_for_status()
        pages = resp.json()["query"]["pages"]
        page = next(iter(pages.values()))
        return page.get("extract", "")
    raise RuntimeError(f"429 nedeniyle vazgeçildi: {title}")


def safe_filename(title: str) -> str:
    return re.sub(r"[^\w\-]+", "_", title).strip("_") + ".txt"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    titles = list_category_members(CATEGORY, MAX_ARTICLES)
    print(f"{len(titles)} madde bulundu.")

    for title in titles:
        out_path = OUT_DIR / safe_filename(title)
        if out_path.exists():
            continue

        text = fetch_plaintext(title)
        if len(text.strip()) < 200:
            continue  # anlamsız/çok kısa maddeleri atla

        out_path.write_text(text, encoding="utf-8")
        print(f"  indirildi: {title}")
        time.sleep(1)  # Wikipedia API'ye nazik davran

    print("Bitti.")


if __name__ == "__main__":
    main()
