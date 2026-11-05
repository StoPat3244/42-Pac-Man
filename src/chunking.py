import ast
import os
from itertools import count
from pathlib import Path
from tqdm import tqdm
from src.models import Chunk

_chunk_counter = count()
_BAR_FORMAT = "{l_bar}{bar:30}{r_bar}"


def _make_chunk(text: str, file_path: str, start: int, end: int) -> Chunk:
    return Chunk(
        file_path=file_path,
        first_character_index=start,
        last_character_index=end - 1,
        text=text,
        chunk_id=str(next(_chunk_counter)),
    )


def _compute_line_offsets(lines: list[str]) -> list[int]:
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    return offsets


def _chunk_python(text: str, file_path: str, max_size: int) -> list[Chunk]:
    try:
        content = ast.parse(text)  # AbstractSyntaxTree
    except SyntaxError:
        return _chunk_by_lines(text, file_path, max_size)
    if not text or text.strip() == "":
        return []
    lines = text.splitlines(keepends=True)
    line_start_offset = _compute_line_offsets(lines)
    blocks: list[tuple[int, int]] = []
    for node in content.body:
        if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
            if node.end_lineno is not None:
                blocks.append((node.lineno, node.end_lineno))

    if not blocks:
        return _chunk_by_lines(text, file_path, max_size)

    def _block_to_chunk(start_line: int, end_line: int) -> None:
        start_char = line_start_offset[start_line - 1]
        if end_line < len(line_start_offset):
            end_char = line_start_offset[end_line]
        else:
            end_char = len(text)
        block_text = text[start_char:end_char]
        if len(block_text) <= max_size:
            chunks.append(
                _make_chunk(block_text, file_path, start_char, end_char))
        else:
            chunks.extend(
                _chunk_by_lines(
                    block_text, file_path, max_size, base_offset=start_char
                )
            )

    chunks: list[Chunk] = []
    is_first = True
    current_start_line: int = 0
    current_end_line: int = 0

    for start_line, end_line in blocks:
        if is_first:
            current_start_line = start_line
            current_end_line = end_line
            is_first = False
            continue
        candidate_start_char = line_start_offset[current_start_line - 1]
        if end_line < len(line_start_offset):
            candidate_end_char = line_start_offset[end_line]
        else:
            candidate_end_char = len(text)
        candidate_size = candidate_end_char - candidate_start_char

        if candidate_size <= max_size:
            current_end_line = end_line
        else:
            _block_to_chunk(current_start_line, current_end_line)
            current_start_line = start_line
            current_end_line = end_line
    _block_to_chunk(current_start_line, current_end_line)

    return chunks


def _chunk_by_lines(text: str, file_path: str, max_size: int,
                    base_offset: int = 0) -> list[Chunk]:
    if not text or text.strip() == "":
        return []
    chunks: list[Chunk] = []
    start = end = 0
    buffer: list[str] = []
    for line in text.splitlines(keepends=True):
        if buffer and end - start + len(line) > max_size:
            chunks.append(
                _make_chunk("".join(buffer), file_path,
                            base_offset + start, base_offset + end))
            buffer = []
            start = end
        if len(line) > max_size:
            pos = 0
            while pos < len(line):
                piece = line[pos:pos + max_size]
                chunks.append(_make_chunk(
                    piece, file_path, base_offset + start + pos,
                    base_offset + start + pos + len(piece)))
                pos += max_size
            start = end + len(line)
            end = start
            continue
        buffer.append(line)
        end += len(line)
    if buffer:
        chunks.append(_make_chunk("".join(buffer), file_path,
                      base_offset + start, base_offset + end))
    return chunks


def _collect_files(root: Path) -> list[Path]:
    allowed_extensions = {".py", ".md", ".txt"}
    files: list[Path] = []
    for current_root, _dirs, filenames in os.walk(root):
        for filename in filenames:
            path = Path(current_root) / filename
            if path.suffix in allowed_extensions:
                files.append(path)
    return files


def get_chunks(root: Path, max_chunk_size: int) -> list[Chunk]:
    all_chunks: list[Chunk] = []
    files = _collect_files(root)
    if not files:
        return []
    for file_path in tqdm(files, desc="Chunking", bar_format=_BAR_FORMAT,
                          ascii=" #"):
        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except PermissionError:
            print(f"\n[WARNING] Permission denied reading file {file_path}")
            continue
        except Exception:
            raise RuntimeError(
                f"[ERROR] An error occurred during reading file "
                f"{file_path}."
            )
        str_path = str(file_path)
        if file_path.suffix == ".py":
            all_chunks.extend(_chunk_python(text, str_path, max_chunk_size))
        else:
            all_chunks.extend(_chunk_by_lines(text, str_path, max_chunk_size))
    return all_chunks
