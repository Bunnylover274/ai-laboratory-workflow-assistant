import math
import os
from pathlib import Path
from typing import TypedDict

from openai import OpenAI


class RetrievedDocument(TypedDict):
    document_id: str
    content: str
    similarity: float


def cosine_similarity(left: list[float], right: list[float]) -> float:
    dot_product = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot_product / (left_norm * right_norm)


def load_documents(directory: Path = Path("knowledge_base")) -> list[tuple[str, str]]:
    documents = [
        (path.stem, path.read_text(encoding="utf-8").strip())
        for path in sorted(directory.glob("*.txt"))
    ]
    if not documents:
        raise FileNotFoundError(f"No .txt documents found in {directory.resolve()}")
    return documents


def retrieve_documents(
    query: str,
    top_k: int = 3,
    required_prefixes: tuple[str, ...] = (),
) -> list[RetrievedDocument]:
    documents = load_documents()
    client = OpenAI()
    model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    inputs = [query] + [content for _, content in documents]

    response = client.embeddings.create(model=model, input=inputs)
    query_vector = response.data[0].embedding
    scored: list[RetrievedDocument] = []

    for (document_id, content), item in zip(documents, response.data[1:]):
        scored.append(
            {
                "document_id": document_id,
                "content": content,
                "similarity": cosine_similarity(query_vector, item.embedding),
            }
        )

    ranked = sorted(scored, key=lambda item: item["similarity"], reverse=True)
    selected = ranked[:top_k]

    for prefix in required_prefixes:
        already_selected = any(
            item["document_id"].upper().startswith(prefix.upper())
            for item in selected
        )
        if already_selected:
            continue

        required_document = next(
            (
                item
                for item in ranked
                if item["document_id"].upper().startswith(prefix.upper())
            ),
            None,
        )
        if required_document is None:
            raise ValueError(f"Required controlled document was not found: {prefix}")
        selected.append(required_document)

    return selected


def format_context(documents: list[RetrievedDocument]) -> str:
    sections = []
    for document in documents:
        sections.append(
            f"[{document['document_id']}]\n{document['content']}"
        )
    return "\n\n".join(sections)
