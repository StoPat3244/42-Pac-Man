from pathlib import Path
from tqdm import tqdm
from src.bm25 import build_bm25_index, load_index, save_index
from src.chunking import get_chunks
from src.cli_parsing import parse_int
from src.generator import build_context, generate_answer, load_generator
from src.models import (
    Chunk,
    MinimalAnswer,
    MinimalSearchResults,
    MinimalSource,
    RagDataset,
    StudentSearchResults,
    StudentSearchResultsAndAnswer,
)
from src.retriever import retrieval_chunks_minsrc, retrieval_chunks

_MIN_CHUNK_SIZE = 49


class CLI:
    _DEFAULT_INDEX_DIR = "data/processed"
    _DEFAULT_RAW_DIR = "data/raw/vllm-0.10.1"

    def index(self, max_chunk_size: int, *unexpected: object,
              **unexpected_kwargs: object) -> None:
        """Build the BM25 index from the raw corpus."""
        parse_int("max_chunk_size", max_chunk_size, 50, 2000,
                  *unexpected, **unexpected_kwargs)

        chunks = get_chunks(Path(self._DEFAULT_RAW_DIR), max_chunk_size)
        if not chunks:
            raise ValueError(f"No files to ingest in {self._DEFAULT_RAW_DIR}.")

        index_bm25 = build_bm25_index(chunks)

        save_index(index_bm25, chunks, Path(self._DEFAULT_INDEX_DIR))
        print(f"Ingestion complete! Indexed {len(chunks)} chunks "
              f"under {self._DEFAULT_INDEX_DIR}")

    def search(self, query: str, k: int, *unexpected: object,
               **unexpected_kwargs: object) -> str:
        """Retrieve the top-k sources for a single query."""
        try:
            parse_int("k", k, 0, 100, *unexpected, **unexpected_kwargs)
            if not isinstance(query, str) or not query.strip():
                raise ValueError("Query must be a string: can't be empty, "
                                 "boolean value or just a number.")
            query = query.strip()

            bm25, chunks = load_index(Path(self._DEFAULT_INDEX_DIR))

            results = retrieval_chunks_minsrc(query, k, bm25, chunks)
            for r in results:
                print(r.file_path,
                      f"[{r.first_character_index}:{r.last_character_index}]")
        except ValueError as e:
            return f"[ERROR]: {e}"
        except Exception as e:
            return f"[ERROR]: {e}"
        return "Search complete!"

    def search_dataset(self, dataset_path: str, k: int,
                       save_directory: str, *unexpected: object,
                       **unexpected_kwargs: object) -> None:
        """Run retrieval on every question of a dataset."""
        try:
            parse_int("k", k, 0, 100, *unexpected, **unexpected_kwargs)

            bm25, chunks = load_index(Path(self._DEFAULT_INDEX_DIR))

            path_dataset = Path(dataset_path)
            questions = path_dataset.read_text(encoding="utf-8")
            model_dataset = RagDataset.model_validate_json(questions)

            search_results = []
            for q in tqdm(model_dataset.rag_questions,
                          desc="search_dataset",
                          bar_format="{l_bar}{bar:30}{r_bar}",
                          ascii=" #"):
                try:
                    sources = retrieval_chunks_minsrc(q.question,
                                                      k, bm25, chunks)
                except Exception as e:
                    print(f"[ERROR] on question_id= {q.question_id}: {e}."
                          " Empty result.")
                    sources = []
                search_results.append(
                    MinimalSearchResults(
                        question_id=q.question_id,
                        question=q.question,
                        retrieved_sources=sources,
                    )
                )

            save_path = Path(save_directory)
            save_path.mkdir(parents=True, exist_ok=True)
            student_results = StudentSearchResults(
                                search_results=search_results,
                                k=k)
            output_path = save_path / path_dataset.name
            output_path.write_text(
                student_results.model_dump_json(indent=2), encoding="utf-8")
            print(f"Saved student_search_results to {output_path}")
        except Exception as e:
            print(f"[ERROR]: {e}")
            return

    def answer(self, query: str, k: int = 10, *unexpected: object,
               **unexpected_kwargs: object) -> None:
        """Answer a single question using retrieved context."""
        try:
            parse_int("k", k, 0, 100, *unexpected, **unexpected_kwargs)
            if not isinstance(query, str) or not query.strip():
                raise ValueError("Query must be a string: can't be empty, "
                                 "boolean value or just a number.")
            query = query.strip()
            bm25, chunks = load_index(Path(self._DEFAULT_INDEX_DIR))
            retrieved_chunks = retrieval_chunks(query, k, bm25, chunks)
            context = build_context(retrieved_chunks)

            generator = load_generator()

            answer_text = generate_answer(query, context, generator)

            sources = [
                MinimalSource(
                    file_path=chunk.file_path,
                    first_character_index=chunk.first_character_index,
                    last_character_index=chunk.last_character_index,
                )
                for chunk in retrieved_chunks
            ]
            output = MinimalAnswer(
                question_id="single_query",
                question=query,
                retrieved_sources=sources,
                answer=answer_text,
            )
            print(output.model_dump_json(indent=2))
        except Exception as e:
            print(f"[ERROR] Generation failed: {e}")
            return

    def answer_dataset(self, student_search_results_path: str,
                       save_directory: str, *unexpected: object,
                       **unexpected_kwargs: object) -> None:
        """Generate answers for a dataset of search results."""
        try:
            parse_int("k", 10, 0, 100, *unexpected, **unexpected_kwargs)

            student_path = Path(student_search_results_path)
            data = StudentSearchResults.model_validate_json(
                student_path.read_text(encoding="utf-8"))
            generator = load_generator()
            answered = []
            for r in tqdm(data.search_results[:5], desc="answer_dataset",
                          bar_format="{l_bar}{bar:30}{r_bar}", ascii=" #",):
                chunks = []
                for s in r.retrieved_sources:
                    try:
                        text = Path(s.file_path).read_text(
                            encoding="utf-8", errors="ignore"
                        )
                        start = s.first_character_index
                        end = s.last_character_index
                        chunks.append(
                            Chunk(
                                file_path=s.file_path,
                                first_character_index=start,
                                last_character_index=end,
                                text=text[start:end],
                                chunk_id="",
                            )
                        )
                    except Exception as e:
                        print(f"ERROR {e}")
                        continue
                context = build_context(chunks)
                answer_text = generate_answer(r.question, context, generator)
                answered.append(
                    MinimalAnswer(
                        question_id=r.question_id,
                        question=r.question,
                        retrieved_sources=r.retrieved_sources,
                        answer=answer_text,
                    )
                )
            output = StudentSearchResultsAndAnswer(search_results=answered,
                                                   k=data.k)
            out_dir = Path(save_directory)
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / student_path.name
            out_path.write_text(output.model_dump_json(indent=2),
                                encoding="utf-8")
            print(f"Saved student_search_results_and_answer to {out_path}")
        except Exception as e:
            print(f"[ERROR] Generation failed: {e}")
            return

    def evaluate(self, student_search_results_path: str, dataset_path: str,
                 k: int = 5, *unexpected: object,
                 **unexpected_kwargs: object) -> None:
        """Compute recall@k of search results against a ground truth."""
        parse_int("k", k, 0, 100, *unexpected, **unexpected_kwargs)

        student = StudentSearchResults.model_validate_json(
            Path(student_search_results_path).read_text()
        )
        truth = RagDataset.model_validate_json(Path(dataset_path).read_text())
        truth_map = {q.question_id: q.sources for q in truth.rag_questions
                     if hasattr(q, "sources")}

        def iou(a: MinimalSource, b: MinimalSource) -> float:
            a_first = a.first_character_index
            a_last = a.last_character_index
            b_first = b.first_character_index
            b_last = b.last_character_index
            inter = max(0, min(a_last, b_last) - max(a_first, b_first))
            if inter <= 0:
                return 0.0
            union = (max(a_last, b_last) - min(a_first, b_first))
            return inter / union if union else 0.0

        recalls = []
        for r in student.search_results:
            gold = truth_map.get(r.question_id, [])
            if not gold:
                continue
            found = sum(
                any(
                    g.file_path == p.file_path and iou(g, p) > 0.05
                    for p in r.retrieved_sources[:k]
                )
                for g in gold
            )
            recalls.append(found / len(gold))
        if recalls:
            print(f"Recall@{k}: {sum(recalls) / len(recalls):.3f}")
        else:
            print("No evaluable questions.")
