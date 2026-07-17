"""Chunking simples para indexação no RAG (Fase 15) — função pura, sem LangChain (não
instalado). Janela fixa de caracteres com sobreposição, conforme docs/21-RAG.md
("Chunk Size: 1000 caracteres. Overlap: 200 caracteres. Nunca gerar chunks
extremamente pequenos.") — para de avançar assim que o último chunk já alcança o fim
do texto, evitando um chunk final minúsculo."""

from __future__ import annotations


def chunk_text(content: str, *, size: int = 1000, overlap: int = 200) -> list[str]:
    content = content.strip()
    if not content:
        return []

    step = size - overlap
    chunks: list[str] = []
    start = 0
    while True:
        end = start + size
        chunks.append(content[start:end])
        if end >= len(content):
            break
        start += step
    return chunks
