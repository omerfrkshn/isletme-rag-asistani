import base64
from pathlib import Path

from anthropic import Anthropic

_MEDIA_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}

_TRANSCRIBE_PROMPT = (
    "Bu görsel taranmış veya el yazısı bir belge. İçindeki tüm metni, "
    "olabildiğince sadık kalarak düz metne çevir. Yorum, açıklama veya "
    "başlık ekleme; sadece transkripsiyonu ver."
)


def load_image(path: Path, client: Anthropic | None = None) -> str:
    client = client or Anthropic()
    media_type = _MEDIA_TYPES[path.suffix.lower()]
    image_b64 = base64.standard_b64encode(path.read_bytes()).decode("utf-8")

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": media_type, "data": image_b64},
                    },
                    {"type": "text", "text": _TRANSCRIBE_PROMPT},
                ],
            }
        ],
    )
    return "".join(block.text for block in response.content if block.type == "text").strip()
