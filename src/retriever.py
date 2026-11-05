from rank_bm25 import BM25Okapi
from src.bm25 import tokenize
from src.models import Chunk, MinimalSource


def retrieval_chunks(query: str, k: int, bm25: BM25Okapi,
                     chunks: list[Chunk]) -> list[Chunk]:
    query_tokens = tokenize(query)
    if not query_tokens:
        raise ValueError("No valid token for this query")

    scores = bm25.get_scores(query_tokens)
    ranked = sorted(zip(chunks, scores), key=lambda pair: pair[1],
                    reverse=True)
    return [chunk for chunk, _score in ranked[:k]]


def retrieval_chunks_minsrc(query: str, k: int, bm25: BM25Okapi,
                            chunks: list[Chunk]
                            ) -> list[MinimalSource]:
    try:
        top_chunks = retrieval_chunks(query, k, bm25, chunks)
    except ValueError as e:
        print(f"[ERROR] = {e}")
        return []
    return [
        MinimalSource(
            file_path=chunk.file_path,
            first_character_index=chunk.first_character_index,
            last_character_index=chunk.last_character_index,
        )
        for chunk in top_chunks
    ]
