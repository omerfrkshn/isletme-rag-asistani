"""Kullanım: python -m src.query.cli kozsofra "Cumartesi kaça kadar açıksınız?" """

import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.answer import answer_question


def main(dataset: str, question: str) -> None:
    load_dotenv()
    result = answer_question(dataset, question)
    print(f"\nCevap: {result['answer']}")
    if result["sources"]:
        print(f"Kaynaklar: {', '.join(result['sources'])}")


if __name__ == "__main__":
    main(sys.argv[1], " ".join(sys.argv[2:]))
