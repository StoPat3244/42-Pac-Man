import sys
from typing import Any

from src.models import Chunk

_DEFAULT_MODEL_NAME = "Qwen/Qwen3-0.6B"
_DEFAULT_MAX_CONTEXT_CHARS = 8000
SYSTEM_PROMPT = (
    "You are a helpful assistant answering questions about the vLLM "
    "codebase. Answer using only the information in the provided "
    "context."
)


def load_generator() -> tuple[Any, Any]:
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as e:
        print(f"[ERROR] Missing dependency: {e}", file=sys.stderr)
        print("[ERROR] Run 'uv sync' to install dependencies.",
              file=sys.stderr)
        sys.exit(1)
    tokenizer = AutoTokenizer.from_pretrained(_DEFAULT_MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(_DEFAULT_MODEL_NAME,
                                                 dtype="auto")
    model.eval()
    return tokenizer, model


def build_context(chunks: list[Chunk]) -> str:
    if not chunks:
        return ""
    chunks_to_text: list[str] = []
    used_chars = 0
    for chunk in chunks:
        text_body = f"Source: {chunk.text}\n."
        remaining = _DEFAULT_MAX_CONTEXT_CHARS - used_chars
        if remaining <= 0:
            break
        chunks_to_text.append(text_body[:remaining])
        used_chars += len(text_body)
    return " --- ".join(chunks_to_text)


def generate_answer(query: str, context: str, generator: tuple[Any, Any],
                    max_new_tokens: int = 300) -> str:
    if not context:
        return "No context for this question."
    try:
        import torch
    except ImportError as e:
        print(f"[ERROR] Missing dependency: {e}", file=sys.stderr)
        print("[ERROR] Run 'uv sync' to install dependencies.",
              file=sys.stderr)
        sys.exit(1)

    tokenizer, model = generator
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",
         "content": f"Context:\n{context}\n\nQuestion: {query}"},
    ]
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True,
        enable_thinking=False)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.inference_mode():
        output = model.generate(**inputs, max_new_tokens=max_new_tokens)
    new_tokens = output[0][inputs["input_ids"].shape[1]:]
    return str(tokenizer.decode(new_tokens, skip_special_tokens=True)).strip()
