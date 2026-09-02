"""Bir veri klasörünü tarar, formatına göre metne çevirir, chunk'lar ve DB'ye yazar.

Kullanım:
    python -m src.ingest.run_ingest kozsofra data/kozsofra
    python -m src.ingest.run_ingest wikipedia data/wikipedia
"""

import sys
from pathlib import Path

from dotenv import load_dotenv
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.embed.db import clear_dataset, init_schema, insert_chunks
from src.embed.embedder import embed_passages
from src.ingest.chunker import chunk_text
from src.ingest.image_loader import load_image
from src.ingest.pdf_loader import load_pdf
from src.ingest.text_loader import load_text

_FORMAT_BY_SUFFIX = {
    ".txt": "text",
    ".md": "text",
    ".pdf": "pdf",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
}


def load_any(path: Path) -> tuple[str, str]:
    fmt = _FORMAT_BY_SUFFIX[path.suffix.lower()]
    if fmt == "text":
        return load_text(path), fmt
    if fmt == "pdf":
        return load_pdf(path), fmt
    return load_image(path), fmt


def main(dataset: str, data_dir: str) -> None:
    load_dotenv()
    init_schema()
    clear_dataset(dataset)

    files = [p for p in Path(data_dir).rglob("*") if p.suffix.lower() in _FORMAT_BY_SUFFIX]
    print(f"{len(files)} dosya bulundu.")

    for path in tqdm(files, desc="ingest"):
        try:
            text, fmt = load_any(path)
        except Exception as exc:  # noqa: BLE001
            print(f"HATA — {path}: {exc}")
            continue

        chunks = chunk_text(text)
        if not chunks:
            continue

        embeddings = embed_passages(chunks)
        rows = [
            {
                "dataset": dataset,
                "source_file": str(path),
                "source_format": fmt,
                "chunk_index": i,
                "content": chunk,
                "embedding": emb,
            }
            for i, (chunk, emb) in enumerate(zip(chunks, embeddings))
        ]
        insert_chunks(rows)

    print("Bitti.")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
