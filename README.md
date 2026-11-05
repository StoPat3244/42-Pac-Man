*This project has been created as part of the 42 curriculum by mcarrara.*

# RAG against the machine

## Description

A simple Retrieval-Augmented Generation (RAG) system that answers questions
about a codebase: the **vLLM 0.10.1** repository.

A language model only knows what it was trained on. Instead of retraining it,
this project lets the model look up information in an external source at
answer time. The pipeline has four stages:

1. **Indexing**: read the corpus, split every file into chunks, build a
   searchable BM25 index and save it to `data/processed/`.
2. **Retrieving**: given a question, return the top-k most relevant snippets
   as source locations (`file_path`, `first_character_index`,
   `last_character_index`).
3. **Augmenting**: put the retrieved snippets into the model's context.
4. **Generating**: `Qwen/Qwen3-0.6B` reads the context and writes an answer.

Retrieval quality is measured with **recall@k** (a source counts as found if
a retrieved chunk is in the same file and overlaps it with IoU > 0.05).

Targets: recall@5 >= 80 % on docs questions, >= 50 % on code questions;
indexing in under 5 minutes; 200 questions searched in under 90 seconds.

## Instructions

### Installation

```bash
uv sync
```

### Project layout

```
.
├── pyproject.toml
├── uv.lock
├── README.md
├── src/
│   ├── __init__.py
│   ├── __main__.py      # entry point (python -m src)
│   ├── cli.py           # Fire CLI: all commands
│   ├── cli_parsing.py   # argument validation
│   ├── chunking.py      # Python and Markdown/text chunking
│   ├── bm25.py          # tokenizer, BM25 index, save/load
│   ├── retriever.py     # top-k retrieval
│   ├── generator.py     # context building and Qwen3 generation
│   └── models.py        # pydantic data models
└── data/
```

### Usage

Every command is run as `uv run python -m src <command> [options]`.

| Command | Description |
|---|---|
| `index --max_chunk_size 2000` | Chunk `data/raw/vllm-0.10.1` and save the BM25 index in `data/processed/` |
| `search "<query>" --k 10` | Print the top-k sources for one query |
| `search_dataset --dataset_path <file> --k 10 --save_directory <dir>` | Retrieve for a whole dataset, write a `StudentSearchResults` JSON |
| `answer "<query>" --k 10` | Retrieve and generate an answer for one query (JSON on stdout) |
| `answer_dataset --student_search_results_path <file> --save_directory <dir>` | Generate answers from a search-results file, write a `StudentSearchResultsAndAnswer` JSON |
| `evaluate --student_search_results_path <file> --dataset_path <file> --k 5` | Compute recall@k against a ground-truth dataset |

### Full pipeline example

```bash
# 1. Index
uv run python -m src index --max_chunk_size 2000

# 2. Search a dataset
uv run python -m src search_dataset \
    --dataset_path data/datasets/UnansweredQuestions/dataset_docs_public.json \
    --k 10 \
    --save_directory data/output/search_results/UnansweredQuestions

# 3. Evaluate (own recall@k; the official one is computed by the moulinette)
uv run python -m src evaluate \
    --student_search_results_path data/output/search_results/UnansweredQuestions/dataset_docs_public.json \
    --dataset_path data/datasets/AnsweredQuestions/dataset_docs_public.json \
    --k 5

# 4. Generate answers
uv run python -m src answer_dataset \
    --student_search_results_path data/output/search_results/UnansweredQuestions/dataset_docs_public.json \
    --save_directory data/output/search_results_and_answer/UnansweredQuestions
```

### Error handling

The CLI validates its inputs and prints an `[ERROR]` message instead of a
traceback for: empty or non-string query, `k` out of range, `max_chunk_size`
out of range, unexpected extra arguments, missing index, missing files and
malformed JSON.

## Technical choices

### Chunking (`src/chunking.py`)

Only `.py`, `.md` and `.txt` files are indexed. Two strategies are used:

- **Python code**: the file is parsed with `ast`. Top-level nodes
  (functions, classes, imports...) are never cut in the middle: consecutive
  nodes are merged into one chunk as long as the chunk stays within
  `max_chunk_size`. A single node larger than the limit is split by lines.
  If the file cannot be parsed (`SyntaxError`), it falls back to line-based
  splitting.
- **Markdown / text**: the text is split line by line, accumulating lines
  until the next one would exceed `max_chunk_size`. A single line longer than
  the limit is cut into fixed-size pieces.

No chunk is ever larger than `max_chunk_size` (default and maximum: 2000
characters), so no retrieved source can exceed the moulinette's
`max_context_length`. Character offsets are stored for every chunk so the
output points back to the exact region of the original file.

### Retrieval (`src/bm25.py`, `src/retriever.py`)

- **BM25** (`rank_bm25.BM25Okapi`) is the implemented lexical method.
- The tokenizer is shared by indexing and querying so both sides match:
  `snake_case` is split on `_`, `camelCase` is split at case boundaries,
  everything is lowercased, tokens shorter than 2 characters and a small set
  of stopwords are removed. This lets a question like "max model len" match
  an identifier such as `max_model_len` or `maxModelLen`.
- The index is saved as `bm25.pkl` (the BM25 object) and `chunks.json` (the
  chunks with their text and offsets). Files are written to temporary files
  first and renamed, so a failed save never leaves a half-written index.
- At query time all chunks are scored and the top-k are returned.

### Generation (`src/generator.py`)

- Model: `Qwen/Qwen3-0.6B` through `transformers` (thinking mode disabled).
- The retrieved chunks are concatenated into a context, capped at 8000
  characters, and passed to the model with a system prompt asking it to answer
  only from the provided context.
- If no context is available, the answer is a fixed "No context for this
  question." message.

### Data models (`src/models.py`)

All data exchanged between stages is validated with pydantic:
`MinimalSource`, `UnansweredQuestion`, `AnsweredQuestion`, `RagDataset`,
`MinimalSearchResults`, `MinimalAnswer`, `StudentSearchResults`,
`StudentSearchResultsAndAnswer`. A `Chunk` model (a `MinimalSource` plus
`chunk_id` and `text`) is added for the index.

## Limitations

- BM25 is purely lexical: a question that paraphrases an idea without using
  the words found in the source can be missed.
- Markdown chunking is line-based and does not follow headings or code
  blocks.
- `Qwen3-0.6B` is a very small model: answers can be partially incomplete.

## Resources

- [vLLM documentation](https://docs.vllm.ai/)
- [BM25 (Okapi BM25)](https://en.wikipedia.org/wiki/Okapi_BM25)
- [rank_bm25](https://github.com/dorianbrown/rank_bm25)
- [Qwen3 model card](https://huggingface.co/Qwen/Qwen3-0.6B)
- [Python `ast` module](https://docs.python.org/3/library/ast.html)
- [Python Fire](https://github.com/google/python-fire)
- [pydantic](https://docs.pydantic.dev/)
- [uv](https://docs.astral.sh/uv/)

### Use of AI

AI was used as a support tool to understand the RAG concepts and to write this README file.
