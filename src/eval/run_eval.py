"""Retrieval doğruluğu, halüsinasyon oranı ve format bazlı başarıyı ölçer.

Kullanım:
    python -m src.eval.run_eval
"""

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.query.answer import answer_question

DATASET_PATH = Path(__file__).parent / "eval_dataset.json"
_REFUSAL_MARKERS = ("bilgim yok", "bilmiyorum")


def _tr_lower(s: str) -> str:
    # Python'ın varsayılan str.lower() Türkçe "İ"yi "i" + birleşen nokta işaretine
    # çevirir (Unicode kuralı), bu da "İçli" gibi kelimelerin küçük harfli
    # karşılıklarıyla eşleşmesini bozar. Türkçe harf eşlemesini elle yapıyoruz.
    return s.replace("İ", "i").replace("I", "ı").lower()


def _is_refusal(answer: str) -> bool:
    lowered = _tr_lower(answer)
    return any(marker in lowered for marker in _REFUSAL_MARKERS)


def run_for_dataset(dataset: str, cases: list[dict]) -> dict:
    total = len(cases)
    retrieval_correct = 0
    hallucinations = 0
    in_scope_cases = [c for c in cases if c["in_scope"]]
    out_of_scope_cases = [c for c in cases if not c["in_scope"]]
    rows = []

    for case in cases:
        result = answer_question(dataset, case["question"])
        source_hit = None
        if case["in_scope"]:
            source_hit = any(
                _tr_lower(case["expected_source_contains"]) in _tr_lower(s) for s in result["sources"]
            )
            if source_hit:
                retrieval_correct += 1
        else:
            if not _is_refusal(result["answer"]):
                hallucinations += 1

        rows.append(
            {
                "question": case["question"],
                "expected_in_scope": case["in_scope"],
                "got_in_scope": result["in_scope"],
                "source_match": source_hit,
                "hallucinated": (not case["in_scope"]) and not _is_refusal(result["answer"]),
                "answer": result["answer"],
            }
        )

    return {
        "dataset": dataset,
        "total": total,
        "retrieval_accuracy": retrieval_correct / len(in_scope_cases) if in_scope_cases else None,
        "hallucination_rate": hallucinations / len(out_of_scope_cases) if out_of_scope_cases else None,
        "rows": rows,
    }


def main() -> None:
    load_dotenv()
    cases_by_dataset = json.loads(DATASET_PATH.read_text(encoding="utf-8"))

    reports = [run_for_dataset(ds, cases) for ds, cases in cases_by_dataset.items()]

    for report in reports:
        print(f"\n== {report['dataset']} ==")
        print(f"Retrieval doğruluğu: {report['retrieval_accuracy']}")
        print(f"Halüsinasyon oranı: {report['hallucination_rate']}")
        for row in report["rows"]:
            ok = row["source_match"] if row["expected_in_scope"] else not row["hallucinated"]
            print(f"  [{'OK' if ok else 'MISS'}] {row['question']}")

    out_path = Path(__file__).parent / "eval_results.json"
    out_path.write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSonuçlar yazıldı: {out_path}")


if __name__ == "__main__":
    main()
