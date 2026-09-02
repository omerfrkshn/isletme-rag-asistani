def chunk_text(text: str, max_chars: int = 800, overlap: int = 150) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) + 2 <= max_chars:
            current = f"{current}\n\n{para}" if current else para
            continue

        if current:
            chunks.append(current)

        if len(para) <= max_chars:
            current = para
        else:
            # tek paragraf çok uzunsa kelime bazlı böl
            words = para.split()
            piece = ""
            for word in words:
                if len(piece) + len(word) + 1 > max_chars:
                    chunks.append(piece)
                    piece = word
                else:
                    piece = f"{piece} {word}" if piece else word
            current = piece

    if current:
        chunks.append(current)

    if overlap and len(chunks) > 1:
        overlapped = [chunks[0]]
        for prev, cur in zip(chunks, chunks[1:]):
            tail = prev[-overlap:]
            overlapped.append(f"{tail} {cur}")
        return overlapped

    return chunks
