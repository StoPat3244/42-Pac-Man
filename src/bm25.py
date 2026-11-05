import json
import pickle
import re
from pathlib import Path
from rank_bm25 import BM25Okapi
from tqdm import tqdm
from src.models import Chunk

STOPWORDS: frozenset[str] = frozenset(
    {
        "the", "a", "an", "is", "are", "of", "to", "in", "and", "or",
        "for", "on", "with", "as", "by", "this", "that", "it", "be",
    }
)
_CAMEL_CASE_SPLIT = re.compile(r"(?<=[a-z0-9]{2})(?=[A-Z])")
_ALPHANUMERIC = re.compile(r"[a-zA-Z0-9]+")
_MIN_TOKEN_LENGTH = 2
_BM25_FILENAME = "bm25.pkl"
_CHUNKS_FILENAME = "chunks.json"


def tokenize(text: str) -> list[str]:
    if not text:
        return []
    text = text.replace("_", " ")
    text = _CAMEL_CASE_SPLIT.sub(" ", text)
    raw_tokens = _ALPHANUMERIC.findall(text)
    return [token.lower() for token in raw_tokens
            if len(token) >= _MIN_TOKEN_LENGTH
            and token.lower() not in STOPWORDS]


def _index_text(chunk: Chunk) -> str:
    return f"{chunk.text}"


def build_bm25_index(chunks: list[Chunk]) -> BM25Okapi:
    tokenized_corpus = [
        tokenize(_index_text(c))
        for c in tqdm(
            chunks,
            desc="Tokenizing",
            bar_format="{l_bar}{bar:30}{r_bar}",
            ascii=" #",
        )
    ]
    return BM25Okapi(tokenized_corpus)


def save_index(bm25: BM25Okapi, chunks: list[Chunk],
               processed_dir: Path) -> None:
    try:
        processed_dir = Path(processed_dir)
        processed_dir.mkdir(parents=True, exist_ok=True)
        bm25_path = processed_dir / _BM25_FILENAME
        chunks_path = processed_dir / _CHUNKS_FILENAME
        bm25_tmp = processed_dir / f"{_BM25_FILENAME}.tmp"
        chunks_tmp = processed_dir / f"{_CHUNKS_FILENAME}.tmp"
        with open(bm25_tmp, "wb") as bm25_file:
            pickle.dump(bm25, bm25_file)
        with open(chunks_tmp, "w", encoding="utf-8") as chunks_file:
            json.dump([chunk.model_dump() for chunk in chunks],
                      chunks_file, indent=4,)
        bm25_tmp.replace(bm25_path)
        chunks_tmp.replace(chunks_path)
    except Exception:
        for tmp_path in (bm25_tmp, chunks_tmp):
            if tmp_path.exists():
                tmp_path.unlink()
        raise RuntimeError(
            f"Error while saving the file from {processed_dir}")


def load_index(processed_dir: Path) -> tuple[BM25Okapi, list[Chunk]]:
    try:
        bm25_path = processed_dir / _BM25_FILENAME
        chunks_path = processed_dir / _CHUNKS_FILENAME
        with open(bm25_path, "rb") as bm25_file:
            bm25: BM25Okapi = pickle.load(bm25_file)
        with open(chunks_path, "r", encoding="utf-8") as chunks_file:
            raw_chunks = json.load(chunks_file)
        chunks = [Chunk(**raw_chunk) for raw_chunk in raw_chunks]
        return bm25, chunks
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format for '{chunks_path}'")
    except FileNotFoundError:
        raise FileNotFoundError(f"Index not found in {processed_dir}. "
                                "Run 'index' command.")
    except Exception:
        raise RuntimeError("Error while loading the file from "
                           f"{processed_dir}")
