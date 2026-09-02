from anthropic import Anthropic

from src.query.retriever import has_relevant_context, retrieve

_SYSTEM_PROMPT = (
    "Sen bir işletmenin müşteri destek asistanısın. Sadece aşağıda verilen "
    "bağlam parçalarındaki bilgiye dayanarak cevap ver. Bağlamda cevap yoksa "
    "ya da bağlam soruyla ilgisizse, uydurma — açıkça 'Bu konuda bilgim yok' de. "
    "Kısa ve net cevap ver."
)


def build_context(results: list[dict]) -> str:
    return "\n\n---\n\n".join(
        f"[Kaynak: {r['source_file']}]\n{r['content']}" for r in results
    )


def answer_question(dataset: str, question: str, client: Anthropic | None = None, top_k: int = 5) -> dict:
    client = client or Anthropic()
    results = retrieve(dataset, question, top_k=top_k)

    if not has_relevant_context(results):
        return {
            "answer": "Bu konuda bilgim yok.",
            "sources": [],
            "in_scope": False,
        }

    context = build_context(results)
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        system=_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Bağlam:\n{context}\n\nSoru: {question}",
            }
        ],
    )
    answer = "".join(block.text for block in response.content if block.type == "text").strip()

    return {
        "answer": answer,
        "sources": [r["source_file"] for r in results],
        "in_scope": True,
    }
